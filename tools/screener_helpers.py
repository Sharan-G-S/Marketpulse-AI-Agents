"""
Screener Formatting Helpers for MarketPulse.

Renders Gainers & Losers screener results as Markdown tables,
summary narratives, and flat dicts for DataFrame display.
"""

from typing import Any, Dict, List

from agents.screener_agent import ScreenerEntry, ScreenerResult, mover_emoji


# ---------------------------------------------------------------------------
# Markdown table
# ---------------------------------------------------------------------------

def format_screener_table(
    entries: List[ScreenerEntry],
    title: str = "Movers",
) -> str:
    """
    Render a list of ScreenerEntry dicts as a Markdown table.

    Columns: Rank | Emoji | Ticker | Price | Change % | Volume | Sector
    """
    if not entries:
        return f"_No {title.lower()} found._"

    header = (
        f"### {title}\n\n"
        "| # | | Ticker | Price | Change % | Volume | Sector |\n"
        "|---|---|--------|-------|----------|--------|--------|"
    )
    rows = [header]
    for i, e in enumerate(entries, 1):
        chg = e.get("change_pct", 0.0)
        sign = "+" if chg > 0 else ""
        vol = e.get("volume")
        vol_str = _fmt_vol(vol)
        rows.append(
            f"| {i} | {mover_emoji(chg)} | **{e['ticker']}** "
            f"| ${e.get('current_price', 0):.2f} "
            f"| {sign}{chg:.2f}% "
            f"| {vol_str} "
            f"| {e.get('sector', 'N/A')} |"
        )
    return "\n".join(rows)


def _fmt_vol(vol: Any) -> str:
    if vol is None:
        return "N/A"
    try:
        v = int(vol)
        if v >= 1_000_000_000:
            return f"{v / 1_000_000_000:.1f}B"
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        if v >= 1_000:
            return f"{v / 1_000:.0f}K"
        return str(v)
    except (ValueError, TypeError):
        return str(vol)


# ---------------------------------------------------------------------------
# Full screener report
# ---------------------------------------------------------------------------

def format_screener_report(result: ScreenerResult) -> str:
    """
    Render a complete Markdown screener report from a ScreenerResult.

    Includes gainers, losers, most-volatile, and market breadth summary.
    """
    sections = [
        "# 📈 Gainers & Losers Screener Report\n",
        format_screener_table(result.get("gainers", []),  "🚀 Top Gainers"),
        "",
        format_screener_table(result.get("losers", []),   "💥 Top Losers"),
        "",
        format_screener_table(result.get("volatile", []), "⚡ Most Volatile"),
        "",
        f"*Scanned {result.get('total_scanned', 0)} tickers — "
        f"generated {result.get('generated_at', '')[:19]} UTC*",
    ]
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Breadth summary narrative
# ---------------------------------------------------------------------------

def format_breadth_summary(breadth: Dict[str, Any]) -> str:
    """
    Render a Markdown breadth summary card.
    """
    if not breadth:
        return "_No breadth data._"

    return (
        f"**Market Breadth:** {breadth.get('breadth_label', 'N/A')}\n\n"
        f"| Advances | Declines | Unchanged | A/D Ratio | Avg Change |\n"
        f"|----------|----------|-----------|-----------|------------|\n"
        f"| {breadth.get('advance_count', 0)} "
        f"| {breadth.get('decline_count', 0)} "
        f"| {breadth.get('unchanged_count', 0)} "
        f"| {breadth.get('advance_decline_ratio', 'N/A')} "
        f"| {breadth.get('avg_change_pct', 0):+.2f}% |"
    )


# ---------------------------------------------------------------------------
# Flat dicts for Streamlit dataframe
# ---------------------------------------------------------------------------

def screener_entries_to_dicts(entries: List[ScreenerEntry]) -> List[Dict[str, Any]]:
    """Flatten ScreenerEntry list into plain dicts for DataFrame display."""
    return [
        {
            "ticker":        e.get("ticker", ""),
            "price":         e.get("current_price"),
            "change_pct":    e.get("change_pct"),
            "volume":        e.get("volume"),
            "market_cap":    e.get("market_cap"),
            "sector":        e.get("sector", "N/A"),
            "rsi":           e.get("rsi"),
        }
        for e in entries
    ]
