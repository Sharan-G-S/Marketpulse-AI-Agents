"""
Alert Engine helpers — formatting and summary utilities.

Provides human-readable formatting for triggered alerts,
severity-based grouping, and a plain-text digest builder.

Works with both:
  - WatchlistTriggeredAlert objects (class-based rule engine)
  - plain alert dicts (function-based evaluate_alerts output)
"""

from typing import Any, Dict, List, Union

from agents.alert_engine import (
    SEVERITY_CRITICAL,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    WatchlistTriggeredAlert,
)

# ---------------------------------------------------------------------------
# Type alias for either alert format
# ---------------------------------------------------------------------------

AnyAlert = Union[WatchlistTriggeredAlert, Dict[str, Any]]

# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

_SEVERITY_ORDER: Dict[str, int] = {
    SEVERITY_CRITICAL: 0,
    SEVERITY_WARNING: 1,
    SEVERITY_INFO: 2,
}

_SEVERITY_ICONS: Dict[str, str] = {
    SEVERITY_CRITICAL: "🔴",
    SEVERITY_WARNING: "🟡",
    SEVERITY_INFO: "🔵",
}


def _get_severity(alert: AnyAlert) -> str:
    """Extract severity string from either alert format."""
    if isinstance(alert, WatchlistTriggeredAlert):
        return str(alert.severity).upper()
    return str(alert.get("severity", SEVERITY_INFO)).upper()


def _get_message(alert: AnyAlert) -> str:
    """Extract message from either alert format."""
    if isinstance(alert, WatchlistTriggeredAlert):
        return alert.message
    return str(alert.get("message", ""))


def _get_timestamp(alert: AnyAlert) -> str:
    """Extract ISO timestamp from either alert format."""
    if isinstance(alert, WatchlistTriggeredAlert):
        return str(alert.triggered_at)
    return str(alert.get("timestamp", ""))


# ---------------------------------------------------------------------------
# Sorting and grouping
# ---------------------------------------------------------------------------

def sort_alerts_by_severity(alerts: List[AnyAlert]) -> List[AnyAlert]:
    """Return alerts sorted from most to least severe."""
    return sorted(alerts, key=lambda a: _SEVERITY_ORDER.get(_get_severity(a), 99))


def group_alerts_by_severity(
    alerts: List[AnyAlert],
) -> Dict[str, List[AnyAlert]]:
    """
    Group a list of alerts by severity label.

    Returns:
        Dict with keys 'critical', 'warning', 'info'.
    """
    groups: Dict[str, List[AnyAlert]] = {
        "critical": [],
        "warning": [],
        "info": [],
    }
    for alert in alerts:
        key = _get_severity(alert).lower()
        if key in groups:
            groups[key].append(alert)
        else:
            groups["info"].append(alert)
    return groups


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_alert_markdown(alert: AnyAlert) -> str:
    """Format a single alert as a Markdown list item."""
    severity = _get_severity(alert)
    icon = _SEVERITY_ICONS.get(severity, "⚪")
    ts = _get_timestamp(alert)
    ts_short = ts[:19].replace("T", " ") if ts else ""
    msg = _get_message(alert)
    suffix = f"  \n  *(evaluated at {ts_short} UTC)*" if ts_short else ""
    return f"- {icon} **[{severity}]** {msg}{suffix}"


def format_alert_digest(alerts: List[AnyAlert]) -> str:
    """
    Build a full plain-text / Markdown digest from a list of alerts.

    Groups alerts by severity and returns a formatted report string.
    Returns a 'no alerts' message if the list is empty.
    """
    if not alerts:
        return "✅ No alerts triggered — all monitored tickers are within normal thresholds."

    sorted_alerts = sort_alerts_by_severity(alerts)
    groups = group_alerts_by_severity(sorted_alerts)

    lines = ["## 🚨 Alert Digest\n"]

    section_map = [
        ("critical", "🔴 Critical Alerts"),
        ("warning", "🟡 Warning Alerts"),
        ("info", "🔵 Info Alerts"),
    ]

    for key, heading in section_map:
        group = groups.get(key, [])
        if group:
            lines.append(f"### {heading}\n")
            for a in group:
                lines.append(format_alert_markdown(a))
            lines.append("")  # blank line between sections

    total = len(alerts)
    n_critical = len(groups["critical"])
    n_warning = len(groups["warning"])
    n_info = len(groups["info"])

    lines.append(
        f"---\n**Summary:** {total} alert(s) — "
        f"{n_critical} critical · {n_warning} warning · {n_info} info"
    )

    return "\n".join(lines)


def ticker_alert_summary(alerts: List[AnyAlert]) -> Dict[str, int]:
    """
    Return a dict mapping ticker → number of alerts triggered.

    Works with both WatchlistTriggeredAlert objects and plain dicts.
    """
    summary: Dict[str, int] = {}
    for alert in alerts:
        if isinstance(alert, WatchlistTriggeredAlert):
            t = alert.rule.ticker
        else:
            t = str(alert.get("ticker", "UNKNOWN"))
        summary[t] = summary.get(t, 0) + 1
    return summary
