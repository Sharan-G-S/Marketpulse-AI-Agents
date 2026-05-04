"""
Sector Heatmap Formatting and Display Helpers for MarketPulse.

Provides Markdown table formatting, color-coding, and summary text
generation from sector heatmap data produced by tools/sector_heatmap.py.
"""

from typing import Any, Dict, List

from tools.sector_heatmap import SectorStats, get_top_and_bottom_sectors


# ---------------------------------------------------------------------------
# Color / emoji helpers
# ---------------------------------------------------------------------------

def heat_score_emoji(score: float) -> str:
    """Return a colour emoji reflecting the sector heat score."""
    if score >= 75:
        return "🔥"
    if score >= 55:
        return "🟢"
    if score >= 45:
        return "⚪"
    if score >= 25:
        return "🔴"
    return "🧊"


def momentum_badge(momentum: str) -> str:
    """Return a short badge string for a momentum label."""
    badges = {
        "Strong Buy":  "▲▲ Strong Buy",
        "Bullish":     "▲  Bullish",
        "Neutral":     "─  Neutral",
        "Bearish":     "▼  Bearish",
        "Strong Sell": "▼▼ Strong Sell",
    }
    return badges.get(momentum, momentum)


# ---------------------------------------------------------------------------
# Markdown table formatter
# ---------------------------------------------------------------------------

def format_heatmap_table(heatmap: List[SectorStats]) -> str:
    """
    Render a sector heatmap as a Markdown table.

    Columns: Rank | Sector | Tickers | Avg Δ% | Avg RSI | Gainers | Heat | Momentum
    """
    if not heatmap:
        return "_No sector data available._"

    header = (
        "| # | Sector | Tickers | Avg Δ% | Avg RSI | Gainers | Heat | Momentum |\n"
        "|---|--------|---------|--------|---------|---------|------|----------|"
    )
    rows = [header]

    for rank, s in enumerate(heatmap, start=1):
        avg_rsi = f"{s['avg_rsi']:.1f}" if s["avg_rsi"] is not None else "N/A"
        emoji = heat_score_emoji(s["heat_score"])
        change_sign = "+" if s["avg_change_pct"] > 0 else ""
        rows.append(
            f"| {rank} | **{s['sector']}** | {s['ticker_count']} | "
            f"{change_sign}{s['avg_change_pct']:.2f}% | {avg_rsi} | "
            f"{s['gainers']}/{s['ticker_count']} | "
            f"{emoji} {s['heat_score']:.1f} | {momentum_badge(s['momentum'])} |"
        )

    return "\n".join(rows)


def format_heatmap_summary(heatmap: List[SectorStats]) -> str:
    """
    Generate a concise plain-text / Markdown summary of sector conditions.

    Highlights the hottest and coolest sectors and gives a market-wide
    breadth reading.
    """
    if not heatmap:
        return "_No sector heatmap data to summarise._"

    tb = get_top_and_bottom_sectors(heatmap, n=2)
    top = tb["top"]
    bottom = tb["bottom"]

    total_tickers = sum(s["ticker_count"] for s in heatmap)
    total_gainers = sum(s["gainers"] for s in heatmap)
    breadth_pct = round(total_gainers / total_tickers * 100, 1) if total_tickers else 0.0

    if breadth_pct >= 65:
        breadth_label = "Broad Market Rally 🟢"
    elif breadth_pct >= 50:
        breadth_label = "Mild Upside Bias ⚪"
    elif breadth_pct >= 35:
        breadth_label = "Mild Downside Pressure ⚠️"
    else:
        breadth_label = "Broad Market Sell-off 🔴"

    lines = [
        "## 🌡️ Sector Heatmap Summary\n",
        f"**Market Breadth:** {breadth_pct:.1f}% gainers across {total_tickers} tickers — *{breadth_label}*\n",
    ]

    if top:
        hot_names = ", ".join(f"**{s['sector']}** ({s['momentum']})" for s in top)
        lines.append(f"**Hottest Sectors:** {hot_names}")

    if bottom:
        cold_names = ", ".join(f"**{s['sector']}** ({s['momentum']})" for s in bottom)
        lines.append(f"**Coolest Sectors:** {cold_names}")

    lines.append(f"\n*Heatmap covers {len(heatmap)} sector(s).*")
    return "\n".join(lines)


def heatmap_to_dicts(heatmap: List[SectorStats]) -> List[Dict[str, Any]]:
    """
    Flatten SectorStats into plain dicts suitable for a Streamlit dataframe
    or CSV export.
    """
    rows = []
    for s in heatmap:
        rows.append({
            "sector": s["sector"],
            "ticker_count": s["ticker_count"],
            "avg_change_pct": s["avg_change_pct"],
            "max_change_pct": s["max_change_pct"],
            "min_change_pct": s["min_change_pct"],
            "avg_rsi": s.get("avg_rsi"),
            "gainers": s["gainers"],
            "losers": s["losers"],
            "heat_score": s["heat_score"],
            "momentum": s["momentum"],
            "tickers": ", ".join(s.get("tickers", [])),
        })
    return rows
