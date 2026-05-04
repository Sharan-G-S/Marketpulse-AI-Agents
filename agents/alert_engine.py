"""
Alert Engine for MarketPulse
Evaluates stock and sentiment data against configurable thresholds
and generates structured alert payloads ready for email or webhook delivery.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from graph.state import MarketPulseState

# ---------------------------------------------------------------------------
# Default alert thresholds — can be overridden at runtime
# ---------------------------------------------------------------------------

DEFAULT_THRESHOLDS: Dict[str, Any] = {
    # RSI extremes
    "rsi_overbought": 70.0,
    "rsi_oversold": 30.0,
    # Single-day price move to trigger an alert
    "price_change_pct": 5.0,
    # Risk levels that always trigger alerts
    "high_risk_levels": {"High", "Critical"},
    # Minimum number of risk flags before alerting
    "min_risk_flags": 3,
    # Sentiment confidence threshold (0–1 scale)
    "low_sentiment_confidence": 0.4,
}


# ---------------------------------------------------------------------------
# Alert severity constants
# ---------------------------------------------------------------------------

SEVERITY_INFO = "INFO"
SEVERITY_WARNING = "WARNING"
SEVERITY_CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Core alert evaluation
# ---------------------------------------------------------------------------


def evaluate_alerts(
    state: Dict[str, Any],
    thresholds: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Evaluate the current MarketPulse state against alert thresholds.

    Args:
        state: A completed MarketPulseState dict (after all agents have run).
        thresholds: Optional override dict for alert thresholds.
                    Unmapped keys fall back to DEFAULT_THRESHOLDS.

    Returns:
        List of alert dicts, each with keys:
            - alert_type (str)
            - severity (str)
            - message (str)
            - value (Any)
            - threshold (Any)
            - ticker (str)
            - timestamp (str ISO-8601)
    """
    cfg = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    alerts: List[Dict[str, Any]] = []
    ticker = state.get("ticker", "UNKNOWN")
    now = datetime.now(timezone.utc).isoformat()

    def _alert(alert_type: str, severity: str, message: str, value: Any, threshold: Any) -> Dict:
        return {
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "value": value,
            "threshold": threshold,
            "ticker": ticker,
            "timestamp": now,
        }

    # -- Risk level check --------------------------------------------------
    risk_level = state.get("risk_level", "")
    if risk_level in cfg["high_risk_levels"]:
        alerts.append(
            _alert(
                "RISK_LEVEL",
                SEVERITY_CRITICAL if risk_level == "Critical" else SEVERITY_WARNING,
                f"{ticker} risk level is {risk_level} — review before trading.",
                risk_level,
                "Medium or lower",
            )
        )

    # -- Risk flag count check ---------------------------------------------
    risk_flags = state.get("risk_flags", [])
    if len(risk_flags) >= cfg["min_risk_flags"]:
        alerts.append(
            _alert(
                "RISK_FLAG_COUNT",
                SEVERITY_WARNING,
                f"{ticker} has {len(risk_flags)} risk flags: {', '.join(risk_flags[:3])}{'...' if len(risk_flags) > 3 else ''}",
                len(risk_flags),
                cfg["min_risk_flags"],
            )
        )

    # -- Price change check ------------------------------------------------
    stock_summary = state.get("stock_summary", {})
    change_pct = stock_summary.get("change_pct")
    if change_pct is not None:
        abs_change = abs(change_pct)
        if abs_change >= cfg["price_change_pct"]:
            direction = "surged" if change_pct > 0 else "dropped"
            alerts.append(
                _alert(
                    "PRICE_MOVE",
                    SEVERITY_WARNING,
                    f"{ticker} {direction} {abs_change:.1f}% today — significant price movement detected.",
                    round(change_pct, 2),
                    cfg["price_change_pct"],
                )
            )

    # -- Sentiment confidence check ----------------------------------------
    sentiment_confidence = state.get("sentiment_confidence", 1.0)
    if sentiment_confidence < cfg["low_sentiment_confidence"]:
        alerts.append(
            _alert(
                "LOW_SENTIMENT_CONFIDENCE",
                SEVERITY_INFO,
                f"{ticker} sentiment confidence is low ({sentiment_confidence:.0%}) — limited news data available.",
                round(sentiment_confidence, 2),
                cfg["low_sentiment_confidence"],
            )
        )

    # -- Bearish sentiment check -------------------------------------------
    overall_sentiment = state.get("overall_sentiment", "")
    if overall_sentiment == "Bearish" and risk_level in ("High", "Critical"):
        alerts.append(
            _alert(
                "BEARISH_HIGH_RISK",
                SEVERITY_CRITICAL,
                f"{ticker} shows Bearish sentiment combined with {risk_level} risk — exercise extreme caution.",
                {"sentiment": overall_sentiment, "risk": risk_level},
                {"sentiment": "Neutral or Bullish", "risk": "Low or Medium"},
            )
        )

    return alerts


# ---------------------------------------------------------------------------
# Alert formatting helpers
# ---------------------------------------------------------------------------


def format_alert_summary(alerts: List[Dict[str, Any]]) -> str:
    """
    Format a list of alerts into a human-readable text summary.

    Returns an empty string if no alerts are present.
    """
    if not alerts:
        return ""

    critical = [a for a in alerts if a["severity"] == SEVERITY_CRITICAL]
    warnings = [a for a in alerts if a["severity"] == SEVERITY_WARNING]
    infos = [a for a in alerts if a["severity"] == SEVERITY_INFO]

    lines = ["MarketPulse Alert Report", "=" * 40]

    if critical:
        lines.append(f"\nCRITICAL ({len(critical)})")
        for a in critical:
            lines.append(f"  [{a['alert_type']}] {a['message']}")

    if warnings:
        lines.append(f"\nWARNING ({len(warnings)})")
        for a in warnings:
            lines.append(f"  [{a['alert_type']}] {a['message']}")

    if infos:
        lines.append(f"\nINFO ({len(infos)})")
        for a in infos:
            lines.append(f"  [{a['alert_type']}] {a['message']}")

    lines.append(f"\nGenerated: {alerts[0]['timestamp']}")
    return "\n".join(lines)


def get_alert_severity_counts(alerts: List[Dict[str, Any]]) -> Dict[str, int]:
    """Return a count of alerts grouped by severity."""
    counts: Dict[str, int] = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 0, SEVERITY_INFO: 0}
    for alert in alerts:
        sev = alert.get("severity", SEVERITY_INFO)
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def has_critical_alerts(alerts: List[Dict[str, Any]]) -> bool:
    """Return True if any alert has CRITICAL severity."""
    return any(a["severity"] == SEVERITY_CRITICAL for a in alerts)


# ---------------------------------------------------------------------------
# Agent wrapper for LangGraph integration
# ---------------------------------------------------------------------------


def alert_agent(state: MarketPulseState) -> MarketPulseState:
    """
    Alert Engine Agent Node.

    Evaluates the completed MarketPulseState against thresholds and
    appends structured alert metadata to the shared state.
    """
    thresholds = state.get("alert_thresholds")
    alerts = evaluate_alerts(state, thresholds=thresholds)
    summary = format_alert_summary(alerts)
    counts = get_alert_severity_counts(alerts)
    critical = has_critical_alerts(alerts)

    return {
        **state,
        "alerts": alerts,
        "alert_summary": summary,
        "alert_counts": counts,
        "has_critical_alerts": critical,
        "alerts_done": True,
        "messages": state.get("messages", []) + [
            f"[Alert Agent] Generated {len(alerts)} alerts (critical: {counts.get(SEVERITY_CRITICAL, 0)})."
        ],
    }


# ---------------------------------------------------------------------------
# Class-based per-ticker rule engine (watchlist / portfolio use-case)
# ---------------------------------------------------------------------------
#
# The function-based evaluate_alerts() above operates on a completed
# LangGraph state for a single ticker.  The classes below provide a
# reusable rule registry that can monitor *many* tickers simultaneously —
# designed for the watchlist and portfolio pages.
# ---------------------------------------------------------------------------

from dataclasses import dataclass, field as _field
from enum import Enum


class WatchlistAlertType(str, Enum):
    """Rule categories supported by WatchlistAlertEngine."""

    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    PERCENT_CHANGE = "percent_change"


@dataclass
class AlertRule:
    """
    A configurable alert rule for a single ticker.

    Attributes:
        ticker:      Uppercase stock symbol, e.g. "AAPL".
        alert_type:  One of the WatchlistAlertType values.
        threshold:   Numeric boundary (price, RSI value, or percent).
        label:       Optional human-readable description.
        severity:    'info', 'warning', or 'critical'.
        enabled:     Whether the rule is active.
    """

    ticker: str
    alert_type: WatchlistAlertType
    threshold: float
    label: str = ""
    severity: str = SEVERITY_WARNING
    enabled: bool = True

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper()
        if not self.label:
            self.label = (
                f"{self.ticker} {self.alert_type.value.replace('_', ' ').title()} "
                f"@ {self.threshold}"
            )


@dataclass
class WatchlistTriggeredAlert:
    """Result produced when an AlertRule fires against live market data."""

    rule: AlertRule
    current_value: float
    message: str
    severity: str
    triggered_at: str = _field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class WatchlistAlertEngine:
    """
    Rule-registry engine that evaluates many tickers in one pass.

    Usage::

        engine = WatchlistAlertEngine.with_default_rules(["AAPL", "TSLA"])
        fired  = engine.evaluate(market_snapshot)
    """

    _DEFAULT_RSI_HIGH = 70.0
    _DEFAULT_RSI_LOW = 30.0
    _DEFAULT_CHG_WARN = 3.0
    _DEFAULT_CHG_CRIT = 7.0

    def __init__(self) -> None:
        self._rules: List[AlertRule] = []

    # -- rule management --------------------------------------------------

    def add_rule(self, rule: AlertRule) -> None:
        """Register a new AlertRule."""
        self._rules.append(rule)

    def remove_rules_for(self, ticker: str) -> None:
        """Remove all rules for *ticker*."""
        self._rules = [r for r in self._rules if r.ticker != ticker.upper()]

    def list_rules(self) -> List[AlertRule]:
        return list(self._rules)

    def clear(self) -> None:
        self._rules.clear()

    # -- evaluation -------------------------------------------------------

    def evaluate(
        self,
        market_snapshot: Dict[str, Dict[str, Any]],
    ) -> List[WatchlistTriggeredAlert]:
        """
        Evaluate all enabled rules against a live market snapshot.

        Args:
            market_snapshot: Dict mapping ticker → data dict with optional
                keys: ``current_price``, ``rsi``, ``change_pct``.

        Returns:
            List of WatchlistTriggeredAlert for all rules that fired.
        """
        fired: List[WatchlistTriggeredAlert] = []

        for rule in self._rules:
            if not rule.enabled:
                continue
            data = market_snapshot.get(rule.ticker, {})
            if not data:
                continue

            result: Optional[WatchlistTriggeredAlert] = None

            if rule.alert_type in (
                WatchlistAlertType.PRICE_ABOVE,
                WatchlistAlertType.PRICE_BELOW,
            ):
                price = data.get("current_price")
                if price is not None:
                    result = self._check_price(rule, float(price))

            elif rule.alert_type in (
                WatchlistAlertType.RSI_OVERBOUGHT,
                WatchlistAlertType.RSI_OVERSOLD,
            ):
                rsi = data.get("rsi")
                if rsi is not None:
                    result = self._check_rsi(rule, float(rsi))

            elif rule.alert_type == WatchlistAlertType.PERCENT_CHANGE:
                chg = data.get("change_pct")
                if chg is not None:
                    result = self._check_change(rule, float(chg))

            if result is not None:
                fired.append(result)

        return fired

    # -- private helpers --------------------------------------------------

    @staticmethod
    def _check_price(
        rule: AlertRule, price: float
    ) -> Optional[WatchlistTriggeredAlert]:
        if rule.alert_type == WatchlistAlertType.PRICE_ABOVE and price > rule.threshold:
            direction = "above"
        elif rule.alert_type == WatchlistAlertType.PRICE_BELOW and price < rule.threshold:
            direction = "below"
        else:
            return None
        msg = (
            f"[{rule.severity.upper()}] {rule.ticker} price ${price:.2f} "
            f"is {direction} threshold ${rule.threshold:.2f}."
        )
        return WatchlistTriggeredAlert(rule=rule, current_value=price, message=msg, severity=rule.severity)

    @staticmethod
    def _check_rsi(
        rule: AlertRule, rsi: float
    ) -> Optional[WatchlistTriggeredAlert]:
        if rule.alert_type == WatchlistAlertType.RSI_OVERBOUGHT and rsi > rule.threshold:
            label = f"overbought (RSI {rsi:.1f} > {rule.threshold})"
        elif rule.alert_type == WatchlistAlertType.RSI_OVERSOLD and rsi < rule.threshold:
            label = f"oversold (RSI {rsi:.1f} < {rule.threshold})"
        else:
            return None
        msg = f"[{rule.severity.upper()}] {rule.ticker} is {label}."
        return WatchlistTriggeredAlert(rule=rule, current_value=rsi, message=msg, severity=rule.severity)

    @staticmethod
    def _check_change(
        rule: AlertRule, change_pct: float
    ) -> Optional[WatchlistTriggeredAlert]:
        if abs(change_pct) < rule.threshold:
            return None
        direction = "surged" if change_pct > 0 else "dropped"
        msg = (
            f"[{rule.severity.upper()}] {rule.ticker} has {direction} "
            f"{change_pct:+.2f}% — exceeds ±{rule.threshold:.1f}% threshold."
        )
        return WatchlistTriggeredAlert(rule=rule, current_value=change_pct, message=msg, severity=rule.severity)

    # -- factory ----------------------------------------------------------

    @classmethod
    def with_default_rules(cls, tickers: List[str]) -> "WatchlistAlertEngine":
        """
        Build a WatchlistAlertEngine pre-loaded with RSI and
        percentage-change rules for each ticker in *tickers*.
        """
        engine = cls()
        for t in tickers:
            t = t.upper()
            engine.add_rule(AlertRule(t, WatchlistAlertType.RSI_OVERBOUGHT, cls._DEFAULT_RSI_HIGH, severity=SEVERITY_WARNING))
            engine.add_rule(AlertRule(t, WatchlistAlertType.RSI_OVERSOLD, cls._DEFAULT_RSI_LOW, severity=SEVERITY_WARNING))
            engine.add_rule(AlertRule(t, WatchlistAlertType.PERCENT_CHANGE, cls._DEFAULT_CHG_WARN, severity=SEVERITY_INFO))
            engine.add_rule(AlertRule(t, WatchlistAlertType.PERCENT_CHANGE, cls._DEFAULT_CHG_CRIT, severity=SEVERITY_CRITICAL))
        return engine
