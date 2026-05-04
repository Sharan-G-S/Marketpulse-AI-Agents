"""
Stock Comparison Formatting Utilities for MarketPulse.

Provides Markdown table rendering and summary text generation
from a ComparisonResult produced by agents/comparison_agent.py.
"""

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Score display helpers
# ---------------------------------------------------------------------------

def score_bar(score: float, width: int = 10) -> str:
    """Render a simple ASCII progress bar for a score (0–100)."""
    filled = round(score / 100.0 * width)
    return "█" * filled + "░" * (width - filled)


def score_emoji(score: float) -> str:
    """Return a colour emoji for a composite score."""
    if score >= 75:
        return "🟢"
    if score >= 55:
        return "🔵"
    if score >= 40:
        return "⚪"
    if score >= 25:
        return "🟡"
    return "🔴"


def label_badge(label: str) -> str:
    """Add a short prefix badge to a score label."""
    badges = {
        "Strong Buy":  "▲▲",
        "Buy":         "▲",
        "Hold":        "─",
        "Sell":        "▼",
        "Strong Sell": "▼▼",
    }
    return f"{badges.get(label, '')} {label}".strip()


# ---------------------------------------------------------------------------
# Markdown table
# ---------------------------------------------------------------------------

def format_comparison_table(result: Dict[str, Any]) -> str:
    """
    Render a side-by-side fundamentals comparison table in Markdown.

    Columns: Metric | Ticker1 | Ticker2 | … (up to 5 tickers)
    """
    tickers = result.get("tickers", [])
    raw = result.get("raw", {})

    if not tickers or not raw:
        return "_No comparison data available._"

    METRICS = [
        ("Price",         "current_price",  lambda v: f"${v:.2f}" if v else "N/A"),
        ("Change 1D",     "change_pct",     lambda v: f"{v:+.2f}%" if v is not None else "N/A"),
        ("Market Cap",    "market_cap",     _fmt_cap),
        ("PE Ratio",      "pe_ratio",       lambda v: f"{v:.1f}" if v else "N/A"),
        ("Beta",          "beta",           lambda v: f"{v:.2f}" if v else "N/A"),
        ("52W High",      "52w_high",       lambda v: f"${v:.2f}" if v else "N/A"),
        ("52W Low",       "52w_low",        lambda v: f"${v:.2f}" if v else "N/A"),
        ("RSI",           "rsi",            lambda v: f"{v:.1f}" if v else "N/A"),
        ("MA Signal",     "ma_signal",      lambda v: v or "N/A"),
        ("Sector",        "sector",         lambda v: v or "N/A"),
        ("Composite Score", "_composite",   None),   # special handling
        ("Recommendation",  "_label",       None),
    ]

    breakdown = result.get("breakdown", {})

    header = "| Metric | " + " | ".join(f"**{t}**" for t in tickers) + " |"
    sep    = "|--------|" + "--------|" * len(tickers)
    rows   = [header, sep]

    for label, key, fmt in METRICS:
        if key == "_composite":
            cells = [
                f"{score_emoji(breakdown.get(t, {}).get('composite', 0))} "
                f"{breakdown.get(t, {}).get('composite', '—')}"
                for t in tickers
            ]
        elif key == "_label":
            cells = [
                label_badge(breakdown.get(t, {}).get("label", "—"))
                for t in tickers
            ]
        else:
            cells = []
            for t in tickers:
                val = raw.get(t, {}).get(key)
                cells.append(fmt(val) if fmt and val is not None else (str(val) if val is not None else "N/A"))

        rows.append("| " + label + " | " + " | ".join(cells) + " |")

    return "\n".join(rows)


def _fmt_cap(cap: Optional[float]) -> str:
    if not cap:
        return "N/A"
    if cap >= 1e12:
        return f"${cap / 1e12:.2f}T"
    if cap >= 1e9:
        return f"${cap / 1e9:.2f}B"
    if cap >= 1e6:
        return f"${cap / 1e6:.2f}M"
    return f"${cap:,.0f}"


# ---------------------------------------------------------------------------
# Rankings summary
# ---------------------------------------------------------------------------

def format_rankings_summary(result: Dict[str, Any]) -> str:
    """Generate a Markdown summary of the comparison rankings."""
    rankings = result.get("rankings", [])
    winner = result.get("winner")

    if not rankings:
        return "_No ranking data available._"

    lines = ["## 🏆 Comparison Rankings\n"]
    medal = ["🥇", "🥈", "🥉"]

    for i, r in enumerate(rankings):
        m = medal[i] if i < 3 else f"**{i+1}.**"
        bar = score_bar(r["score"])
        lines.append(
            f"{m} **{r['ticker']}** — {r['score']:.1f}/100 `{bar}` "
            f"_{label_badge(r['label'])}_"
        )

    if winner:
        lines.append(f"\n> 🏅 **{winner}** scores highest across all weighted dimensions.")

    lines.append(f"\n*Generated: {result.get('generated_at', '')[:19]} UTC*")
    return "\n".join(lines)


def format_score_breakdown_table(result: Dict[str, Any]) -> str:
    """Render a score component breakdown table per ticker."""
    breakdown = result.get("breakdown", {})
    tickers = result.get("tickers", [])

    if not breakdown or not tickers:
        return "_No breakdown data._"

    rows = [
        "| Component | Weight | " + " | ".join(f"**{t}**" for t in tickers) + " |",
        "|-----------|--------|" + "--------|" * len(tickers),
    ]

    components = [
        ("Momentum",   "momentum_score",  "25%"),
        ("Valuation",  "valuation_score", "20%"),
        ("Technical",  "technical_score", "25%"),
        ("Stability",  "stability_score", "15%"),
        ("52W Range",  "range_score",     "15%"),
    ]

    for label, key, weight in components:
        cells = [f"{breakdown.get(t, {}).get(key, 0):.1f}" for t in tickers]
        rows.append(f"| {label} | {weight} | " + " | ".join(cells) + " |")

    # Totals
    totals = [f"**{breakdown.get(t, {}).get('composite', 0):.1f}**" for t in tickers]
    rows.append("| **Composite** | **100%** | " + " | ".join(totals) + " |")

    return "\n".join(rows)
