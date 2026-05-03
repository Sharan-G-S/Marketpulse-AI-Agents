"""
Alert Engine — Core module for MarketPulse.

Defines alert rules (price threshold and RSI-based) and evaluates
them against live market data to surface actionable notifications
without requiring an LLM call.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums & constants
# ---------------------------------------------------------------------------


class AlertType(str, Enum):
    """Supported alert rule categories."""

    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    PERCENT_CHANGE = "percent_change"


class AlertSeverity(str, Enum):
    """Severity levels for triggered alerts."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# Default RSI threshold defaults (industry standard)
DEFAULT_RSI_OVERBOUGHT = 70.0
DEFAULT_RSI_OVERSOLD = 30.0

# Default percentage-change thresholds
DEFAULT_CHANGE_WARNING_PCT = 3.0   # ±3 %
DEFAULT_CHANGE_CRITICAL_PCT = 7.0  # ±7 %


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class AlertRule:
    """
    A single alert rule definition.

    Attributes:
        ticker:      Stock ticker symbol (e.g. "AAPL").
        alert_type:  One of the AlertType enum values.
        threshold:   Numeric threshold for price/RSI/percent rules.
        label:       Human-readable rule description.
        severity:    Severity level if triggered.
        enabled:     Whether the rule is active.
    """

    ticker: str
    alert_type: AlertType
    threshold: float
    label: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    enabled: bool = True

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper()
        if not self.label:
            self.label = (
                f"{self.ticker} {self.alert_type.value.replace('_', ' ').title()} "
                f"@ {self.threshold}"
            )


@dataclass
class TriggeredAlert:
    """
    Result produced when an AlertRule fires.

    Attributes:
        rule:          The AlertRule that was triggered.
        current_value: The live value that crossed the threshold.
        message:       Human-readable alert message.
        severity:      Severity of the alert.
        triggered_at:  ISO-8601 UTC timestamp when evaluated.
    """

    rule: AlertRule
    current_value: float
    message: str
    severity: AlertSeverity
    triggered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Alert evaluation helpers
# ---------------------------------------------------------------------------


def _evaluate_price_rule(
    rule: AlertRule,
    current_price: float,
) -> Optional[TriggeredAlert]:
    """Check price-threshold rules (PRICE_ABOVE / PRICE_BELOW)."""
    triggered = False
    if rule.alert_type == AlertType.PRICE_ABOVE and current_price > rule.threshold:
        triggered = True
        direction = "above"
    elif rule.alert_type == AlertType.PRICE_BELOW and current_price < rule.threshold:
        triggered = True
        direction = "below"

    if not triggered:
        return None

    msg = (
        f"[{rule.severity.value.upper()}] {rule.ticker} price ${current_price:.2f} "
        f"is {direction} threshold ${rule.threshold:.2f}."
    )
    return TriggeredAlert(
        rule=rule,
        current_value=current_price,
        message=msg,
        severity=rule.severity,
    )


def _evaluate_rsi_rule(
    rule: AlertRule,
    rsi: float,
) -> Optional[TriggeredAlert]:
    """Check RSI-based rules (RSI_OVERBOUGHT / RSI_OVERSOLD)."""
    triggered = False
    condition_label = ""
    if rule.alert_type == AlertType.RSI_OVERBOUGHT and rsi > rule.threshold:
        triggered = True
        condition_label = f"overbought (RSI {rsi:.1f} > {rule.threshold})"
    elif rule.alert_type == AlertType.RSI_OVERSOLD and rsi < rule.threshold:
        triggered = True
        condition_label = f"oversold (RSI {rsi:.1f} < {rule.threshold})"

    if not triggered:
        return None

    msg = (
        f"[{rule.severity.value.upper()}] {rule.ticker} is {condition_label}. "
        f"Consider reviewing position."
    )
    return TriggeredAlert(
        rule=rule,
        current_value=rsi,
        message=msg,
        severity=rule.severity,
    )


def _evaluate_change_rule(
    rule: AlertRule,
    change_pct: float,
) -> Optional[TriggeredAlert]:
    """Check percentage-change rules (PERCENT_CHANGE)."""
    if abs(change_pct) < rule.threshold:
        return None

    direction = "surged" if change_pct > 0 else "dropped"
    msg = (
        f"[{rule.severity.value.upper()}] {rule.ticker} has {direction} "
        f"{change_pct:+.2f}% — exceeds ±{rule.threshold:.1f}% threshold."
    )
    return TriggeredAlert(
        rule=rule,
        current_value=change_pct,
        message=msg,
        severity=rule.severity,
    )


# ---------------------------------------------------------------------------
# AlertEngine
# ---------------------------------------------------------------------------


class AlertEngine:
    """
    Manages a registry of AlertRules and evaluates them against
    live market snapshots.

    Usage::

        engine = AlertEngine()
        engine.add_rule(AlertRule("AAPL", AlertType.PRICE_BELOW, 170.0))
        engine.add_rule(AlertRule("TSLA", AlertType.RSI_OVERBOUGHT, 70.0))

        triggered = engine.evaluate(market_snapshot)
    """

    def __init__(self) -> None:
        self._rules: List[AlertRule] = []

    # ------------------------------------------------------------------
    # Rule management
    # ------------------------------------------------------------------

    def add_rule(self, rule: AlertRule) -> None:
        """Register a new alert rule."""
        self._rules.append(rule)

    def remove_rules_for(self, ticker: str) -> None:
        """Remove all rules associated with *ticker*."""
        ticker = ticker.upper()
        self._rules = [r for r in self._rules if r.ticker != ticker]

    def list_rules(self) -> List[AlertRule]:
        """Return a copy of the current rule registry."""
        return list(self._rules)

    def clear(self) -> None:
        """Remove all rules."""
        self._rules.clear()

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        market_snapshot: Dict[str, Dict[str, Any]],
    ) -> List[TriggeredAlert]:
        """
        Evaluate all enabled rules against *market_snapshot*.

        Args:
            market_snapshot: Dict mapping ticker → data dict.
                Expected keys per ticker:
                    - ``current_price`` (float)
                    - ``rsi``           (float, optional)
                    - ``change_pct``    (float, optional)

        Returns:
            List of TriggeredAlert objects for all fired rules.
        """
        fired: List[TriggeredAlert] = []

        for rule in self._rules:
            if not rule.enabled:
                continue

            ticker_data = market_snapshot.get(rule.ticker, {})
            if not ticker_data:
                continue

            result: Optional[TriggeredAlert] = None

            if rule.alert_type in (AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW):
                price = ticker_data.get("current_price")
                if price is not None:
                    result = _evaluate_price_rule(rule, float(price))

            elif rule.alert_type in (AlertType.RSI_OVERBOUGHT, AlertType.RSI_OVERSOLD):
                rsi = ticker_data.get("rsi")
                if rsi is not None:
                    result = _evaluate_rsi_rule(rule, float(rsi))

            elif rule.alert_type == AlertType.PERCENT_CHANGE:
                change = ticker_data.get("change_pct")
                if change is not None:
                    result = _evaluate_change_rule(rule, float(change))

            if result is not None:
                fired.append(result)

        return fired

    # ------------------------------------------------------------------
    # Default rule factory
    # ------------------------------------------------------------------

    @classmethod
    def with_default_rules(cls, tickers: List[str]) -> "AlertEngine":
        """
        Create an AlertEngine pre-loaded with sensible default rules
        for each ticker in *tickers*.

        Default rules per ticker:
            - RSI overbought > 70  (WARNING)
            - RSI oversold   < 30  (WARNING)
            - Price change   ±3 %  (INFO)
            - Price change   ±7 %  (CRITICAL)
        """
        engine = cls()
        for t in tickers:
            t = t.upper()
            engine.add_rule(AlertRule(
                ticker=t,
                alert_type=AlertType.RSI_OVERBOUGHT,
                threshold=DEFAULT_RSI_OVERBOUGHT,
                severity=AlertSeverity.WARNING,
            ))
            engine.add_rule(AlertRule(
                ticker=t,
                alert_type=AlertType.RSI_OVERSOLD,
                threshold=DEFAULT_RSI_OVERSOLD,
                severity=AlertSeverity.WARNING,
            ))
            engine.add_rule(AlertRule(
                ticker=t,
                alert_type=AlertType.PERCENT_CHANGE,
                threshold=DEFAULT_CHANGE_WARNING_PCT,
                severity=AlertSeverity.INFO,
            ))
            engine.add_rule(AlertRule(
                ticker=t,
                alert_type=AlertType.PERCENT_CHANGE,
                threshold=DEFAULT_CHANGE_CRITICAL_PCT,
                severity=AlertSeverity.CRITICAL,
            ))
        return engine
