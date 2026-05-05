"""
Gainers & Losers Screener Agent for MarketPulse.

Scans a configurable ticker universe, fetches 1-day price changes,
and ranks tickers as top gainers, top losers, and most-volatile —
without any LLM calls.

Designed to run as a standalone utility or as part of the Streamlit UI.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Default ticker universe — S&P 500 large-caps across major sectors
# ---------------------------------------------------------------------------

SCREENER_UNIVERSE = [
    # Technology
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "TSLA", "AMD", "INTC", "QCOM", "AVGO",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT",
    # Financials
    "JPM", "BAC", "WFC", "GS", "MS", "BLK", "SCHW",
    # Consumer
    "AMZN", "HD", "MCD", "NKE", "SBUX", "TGT", "WMT",
    # Energy
    "XOM", "CVX", "COP", "SLB",
    # Industrials
    "BA", "CAT", "GE", "HON", "UPS",
    # Communications
    "NFLX", "DIS", "T", "VZ",
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

ScreenerEntry = Dict[str, Any]
"""
{
    "ticker":       str,
    "company_name": str,
    "sector":       str,
    "current_price": float,
    "change_pct":   float,
    "volume":       int,
    "market_cap":   float | None,
    "rsi":          float | None,
    "screened_at":  str  (ISO-8601)
}
"""

ScreenerResult = Dict[str, Any]
"""
{
    "gainers":    List[ScreenerEntry],
    "losers":     List[ScreenerEntry],
    "volatile":   List[ScreenerEntry],
    "flat":       List[ScreenerEntry],
    "total_scanned": int,
    "generated_at":  str,
}
"""


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def classify_mover(change_pct: float) -> str:
    """Classify a ticker's daily move into a bucket label."""
    if change_pct >= 5.0:
        return "Strong Gainer"
    if change_pct >= 2.0:
        return "Gainer"
    if change_pct <= -5.0:
        return "Strong Loser"
    if change_pct <= -2.0:
        return "Loser"
    return "Flat"


def mover_emoji(change_pct: float) -> str:
    """Return a colour emoji for a mover's daily change."""
    if change_pct >= 5.0:
        return "🚀"
    if change_pct >= 2.0:
        return "🟢"
    if change_pct >= 0:
        return "🔼"
    if change_pct >= -2.0:
        return "🔽"
    if change_pct >= -5.0:
        return "🔴"
    return "💥"


# ---------------------------------------------------------------------------
# Core screener
# ---------------------------------------------------------------------------

def run_screener(
    entries: List[ScreenerEntry],
    top_n: int = 5,
) -> ScreenerResult:
    """
    Rank a list of pre-fetched ScreenerEntry dicts into gainers, losers,
    most-volatile, and flat movers.

    Args:
        entries: List of ScreenerEntry dicts (already enriched with price data).
        top_n:   How many tickers to include in each ranked group.

    Returns:
        ScreenerResult dict.
    """
    valid = [e for e in entries if e.get("change_pct") is not None]

    # Sort by change % descending for gainers, ascending for losers
    by_change = sorted(valid, key=lambda x: x["change_pct"], reverse=True)
    gainers   = [e for e in by_change if e["change_pct"] > 0][:top_n]
    losers    = sorted(valid, key=lambda x: x["change_pct"])[:top_n]
    losers    = [e for e in losers if e["change_pct"] < 0]

    # Most volatile = highest absolute move regardless of direction
    volatile = sorted(valid, key=lambda x: abs(x["change_pct"]), reverse=True)[:top_n]

    # Flat = smallest absolute move
    flat = sorted(valid, key=lambda x: abs(x["change_pct"]))[:top_n]

    return {
        "gainers":       gainers,
        "losers":        losers,
        "volatile":      volatile,
        "flat":          flat,
        "total_scanned": len(entries),
        "generated_at":  datetime.now(timezone.utc).isoformat(),
    }


def screener_breadth(entries: List[ScreenerEntry]) -> Dict[str, Any]:
    """
    Compute market breadth statistics from screener entries.

    Returns:
        Dict with advance_count, decline_count, unchanged_count,
        advance_decline_ratio, avg_change_pct, and breadth_label.
    """
    valid = [e for e in entries if e.get("change_pct") is not None]
    if not valid:
        return {}

    advances  = sum(1 for e in valid if e["change_pct"] > 0)
    declines  = sum(1 for e in valid if e["change_pct"] < 0)
    unchanged = len(valid) - advances - declines
    avg_chg   = round(sum(e["change_pct"] for e in valid) / len(valid), 2)
    ad_ratio  = round(advances / declines, 2) if declines else float("inf")

    if advances >= declines * 2:
        breadth_label = "Strong Advance 🟢"
    elif advances > declines:
        breadth_label = "Moderate Advance ⬆️"
    elif declines >= advances * 2:
        breadth_label = "Strong Decline 🔴"
    elif declines > advances:
        breadth_label = "Moderate Decline ⬇️"
    else:
        breadth_label = "Balanced ⚪"

    return {
        "advance_count":        advances,
        "decline_count":        declines,
        "unchanged_count":      unchanged,
        "advance_decline_ratio": ad_ratio,
        "avg_change_pct":       avg_chg,
        "breadth_label":        breadth_label,
    }
