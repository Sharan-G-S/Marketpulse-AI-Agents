"""
Watchlist Price Alert Engine for MarketPulse.

Monitors a list of tickers against user-defined price thresholds and
generates structured alerts when conditions are breached — without any LLM.

Supports:
  - price_above  / price_below  absolute thresholds
  - change_pct_above / change_pct_below  percentage move thresholds
  - rsi_overbought / rsi_oversold  RSI thresholds
  - volume_spike  (today's volume vs average volume ratio)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ── Types ────────────────────────────────────────────────────────────────────

WatchlistEntry = Dict[str, Any]
"""
{
    "ticker":        str,
    "current_price": float,
    "change_pct":    float,
    "volume":        int | None,
    "avg_volume":    int | None,
    "rsi":           float | None,
    "thresholds":    dict  # per-ticker overrides (optional)
}
"""

AlertRecord = Dict[str, Any]
"""
{
    "ticker":      str,
    "alert_type":  str,
    "severity":    "CRITICAL" | "WARNING" | "INFO",
    "message":     str,
    "value":       float,
    "threshold":   float,
    "timestamp":   str  (ISO-8601)
}
"""

# ── Default thresholds ────────────────────────────────────────────────────────

DEFAULT_WATCHLIST_THRESHOLDS: Dict[str, float] = {
    "price_change_pct": 5.0,      # alert if daily move ≥ ±5 %
    "rsi_overbought":   75.0,     # alert if RSI ≥ 75
    "rsi_oversold":     25.0,     # alert if RSI ≤ 25
    "volume_spike":     2.0,      # alert if volume ≥ 2× avg volume
}


# ── Alert severity ────────────────────────────────────────────────────────────

SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_WARNING  = "WARNING"
SEVERITY_INFO     = "INFO"


# ── Core alert evaluation ─────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_alert(
    ticker: str,
    alert_type: str,
    severity: str,
    message: str,
    value: float,
    threshold: float,
) -> AlertRecord:
    return {
        "ticker":     ticker.upper(),
        "alert_type": alert_type,
        "severity":   severity,
        "message":    message,
        "value":      value,
        "threshold":  threshold,
        "timestamp":  _now(),
    }


def evaluate_watchlist_entry(
    entry: WatchlistEntry,
    thresholds: Optional[Dict[str, float]] = None,
) -> List[AlertRecord]:
    """
    Evaluate a single watchlist entry against price/RSI/volume thresholds.

    Args:
        entry:      WatchlistEntry dict with current market data.
        thresholds: Override thresholds dict (merged with defaults).

    Returns:
        List of AlertRecord dicts (may be empty).
    """
    t = {**DEFAULT_WATCHLIST_THRESHOLDS, **(thresholds or {})}
    t.update(entry.get("thresholds", {}))

    alerts: List[AlertRecord] = []
    ticker = entry.get("ticker", "???").upper()
    chg    = entry.get("change_pct", 0.0) or 0.0
    price  = entry.get("current_price", 0.0) or 0.0
    rsi    = entry.get("rsi")
    vol    = entry.get("volume")
    avg_vol = entry.get("avg_volume")

    # ── Price change spike ────────────────────────────────────────────────────
    pct_thresh = t["price_change_pct"]
    if abs(chg) >= pct_thresh:
        direction = "surged" if chg > 0 else "dropped"
        severity = SEVERITY_CRITICAL if abs(chg) >= pct_thresh * 1.5 else SEVERITY_WARNING
        alerts.append(_make_alert(
            ticker, "PRICE_CHANGE",
            severity,
            f"{ticker} has {direction} {chg:+.2f}% today (threshold ±{pct_thresh:.1f}%)",
            chg, pct_thresh,
        ))

    # ── Absolute price thresholds (user-supplied only) ────────────────────────
    if "price_above" in t and price >= t["price_above"]:
        alerts.append(_make_alert(
            ticker, "PRICE_ABOVE",
            SEVERITY_INFO,
            f"{ticker} price ${price:.2f} crossed above ${t['price_above']:.2f}",
            price, t["price_above"],
        ))
    if "price_below" in t and price <= t["price_below"]:
        alerts.append(_make_alert(
            ticker, "PRICE_BELOW",
            SEVERITY_WARNING,
            f"{ticker} price ${price:.2f} fell below ${t['price_below']:.2f}",
            price, t["price_below"],
        ))

    # ── RSI overbought / oversold ────────────────────────────────────────────
    if rsi is not None:
        if rsi >= t["rsi_overbought"]:
            alerts.append(_make_alert(
                ticker, "RSI_OVERBOUGHT",
                SEVERITY_WARNING,
                f"{ticker} RSI {rsi:.1f} is overbought (≥ {t['rsi_overbought']:.0f})",
                rsi, t["rsi_overbought"],
            ))
        elif rsi <= t["rsi_oversold"]:
            alerts.append(_make_alert(
                ticker, "RSI_OVERSOLD",
                SEVERITY_INFO,
                f"{ticker} RSI {rsi:.1f} is oversold (≤ {t['rsi_oversold']:.0f})",
                rsi, t["rsi_oversold"],
            ))

    # ── Volume spike ─────────────────────────────────────────────────────────
    if vol and avg_vol and avg_vol > 0:
        ratio = vol / avg_vol
        if ratio >= t["volume_spike"]:
            alerts.append(_make_alert(
                ticker, "VOLUME_SPIKE",
                SEVERITY_INFO,
                f"{ticker} volume {ratio:.1f}× above average (threshold {t['volume_spike']:.1f}×)",
                ratio, t["volume_spike"],
            ))

    return alerts


def evaluate_watchlist(
    entries: List[WatchlistEntry],
    global_thresholds: Optional[Dict[str, float]] = None,
) -> List[AlertRecord]:
    """
    Evaluate all watchlist entries and return a flat list of all alerts,
    sorted by severity (CRITICAL first) then ticker.
    """
    all_alerts: List[AlertRecord] = []
    for entry in entries:
        all_alerts.extend(evaluate_watchlist_entry(entry, global_thresholds))

    severity_order = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 1, SEVERITY_INFO: 2}
    all_alerts.sort(key=lambda a: (severity_order.get(a["severity"], 3), a["ticker"]))
    return all_alerts


def watchlist_alert_summary(alerts: List[AlertRecord]) -> Dict[str, Any]:
    """Return count breakdown and a human-readable status string."""
    counts = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 0, SEVERITY_INFO: 0}
    for a in alerts:
        counts[a["severity"]] = counts.get(a["severity"], 0) + 1

    if counts[SEVERITY_CRITICAL]:
        status = f"🔴 {counts[SEVERITY_CRITICAL]} critical alert(s) require attention"
    elif counts[SEVERITY_WARNING]:
        status = f"🟡 {counts[SEVERITY_WARNING]} warning(s) detected"
    elif counts[SEVERITY_INFO]:
        status = f"🔵 {counts[SEVERITY_INFO]} informational alert(s)"
    else:
        status = "🟢 All watchlist tickers within normal ranges"

    return {"counts": counts, "status": status, "total": len(alerts)}

# ── Public API ────────────────────────────────────────────────────────────────
__all__ = [
    "DEFAULT_WATCHLIST_THRESHOLDS",
    "SEVERITY_CRITICAL",
    "SEVERITY_WARNING",
    "SEVERITY_INFO",
    "evaluate_watchlist_entry",
    "evaluate_watchlist",
    "watchlist_alert_summary",
]
