"""
Alert Engine for MarketPulse
Evaluates stock and sentiment data against configurable thresholds
and generates structured alert payloads ready for email or webhook delivery.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
