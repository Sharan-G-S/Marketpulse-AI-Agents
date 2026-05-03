"""
Alert Engine helpers — formatting and summary utilities.

Provides human-readable formatting for triggered alerts,
severity-based grouping, and a plain-text digest builder.
"""

from typing import Dict, List

from agents.alert_engine import AlertSeverity, TriggeredAlert


# ---------------------------------------------------------------------------
# Severity ordering for sorting
# ---------------------------------------------------------------------------

_SEVERITY_ORDER: Dict[AlertSeverity, int] = {
    AlertSeverity.CRITICAL: 0,
    AlertSeverity.WARNING: 1,
    AlertSeverity.INFO: 2,
}


def sort_alerts_by_severity(alerts: List[TriggeredAlert]) -> List[TriggeredAlert]:
    """Return alerts sorted from most to least severe."""
    return sorted(alerts, key=lambda a: _SEVERITY_ORDER.get(a.severity, 99))


def group_alerts_by_severity(
    alerts: List[TriggeredAlert],
) -> Dict[str, List[TriggeredAlert]]:
    """
    Group a list of TriggeredAlert objects by severity label.

    Returns:
        Dict with keys 'critical', 'warning', 'info'.
    """
    groups: Dict[str, List[TriggeredAlert]] = {
        "critical": [],
        "warning": [],
        "info": [],
    }
    for alert in alerts:
        groups[alert.severity.value].append(alert)
    return groups


def format_alert_markdown(alert: TriggeredAlert) -> str:
    """Format a single TriggeredAlert as a Markdown list item."""
    icons = {
        AlertSeverity.CRITICAL: "🔴",
        AlertSeverity.WARNING: "🟡",
        AlertSeverity.INFO: "🔵",
    }
    icon = icons.get(alert.severity, "⚪")
    ts = alert.triggered_at[:19].replace("T", " ")  # YYYY-MM-DD HH:MM:SS
    return f"- {icon} **[{alert.severity.value.upper()}]** {alert.message}  \n  *(evaluated at {ts} UTC)*"


def format_alert_digest(alerts: List[TriggeredAlert]) -> str:
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


def ticker_alert_summary(alerts: List[TriggeredAlert]) -> Dict[str, int]:
    """
    Return a dict mapping ticker → number of alerts triggered.

    Useful for highlighting tickers that need immediate attention.
    """
    summary: Dict[str, int] = {}
    for alert in alerts:
        t = alert.rule.ticker
        summary[t] = summary.get(t, 0) + 1
    return summary
