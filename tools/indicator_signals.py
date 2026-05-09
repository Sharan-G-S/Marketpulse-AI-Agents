"""
Indicator Signal Helpers for MarketPulse.

Wraps raw indicator values (RSI, MACD, Bollinger Bands, MA crossovers)
into human-readable signals, badges, and Markdown summary tables.
"""

from typing import Any, Dict, List, Optional

# ── RSI ──────────────────────────────────────────────────────────────────────

def rsi_signal(rsi: Optional[float]) -> str:
    if rsi is None:
        return "N/A"
    if rsi >= 75:
        return "🔴 Overbought"
    if rsi >= 60:
        return "🟡 Bullish"
    if rsi <= 25:
        return "🔵 Oversold"
    if rsi <= 40:
        return "🟡 Bearish"
    return "⚪ Neutral"


# ── MACD ──────────────────────────────────────────────────────────────────────

def macd_signal(macd: Optional[Dict[str, Any]]) -> str:
    if not macd:
        return "N/A"
    crossover = macd.get("crossover", "")
    if "Bullish" in crossover:
        return "🟢 Bullish Crossover"
    if "Bearish" in crossover:
        return "🔴 Bearish Crossover"
    val  = macd.get("macd", 0) or 0
    sig  = macd.get("signal", 0) or 0
    if val > sig:
        return "🟡 Bullish (above signal)"
    if val < sig:
        return "🟡 Bearish (below signal)"
    return "⚪ Neutral"


# ── Moving averages ───────────────────────────────────────────────────────────

def ma_signal(ma_signal_str: Optional[str]) -> str:
    if not ma_signal_str:
        return "N/A"
    if "Golden" in ma_signal_str:
        return "🟢 Golden Cross (Bullish)"
    if "Death" in ma_signal_str:
        return "🔴 Death Cross (Bearish)"
    return f"⚪ {ma_signal_str}"


# ── Bollinger Bands ───────────────────────────────────────────────────────────

def bollinger_signal(bb: Optional[Dict[str, Any]], current_price: float) -> str:
    if not bb or not current_price:
        return "N/A"
    upper = bb.get("upper") or 0
    lower = bb.get("lower") or 0
    mid   = bb.get("middle") or 0
    if not upper or not lower:
        return "N/A"
    if current_price >= upper:
        return "🔴 Near Upper Band (Overbought)"
    if current_price <= lower:
        return "🟢 Near Lower Band (Oversold)"
    if current_price > mid:
        return "🟡 Above Middle Band"
    return "🟡 Below Middle Band"


# ── Overall signal ────────────────────────────────────────────────────────────

def overall_signal(rsi: Optional[float], macd: Optional[Dict], ma_str: Optional[str]) -> str:
    """Simple vote-based overall signal from RSI, MACD, and MA cross."""
    bullish = 0
    bearish = 0

    if rsi is not None:
        if rsi < 40:
            bullish += 1
        elif rsi > 65:
            bearish += 1

    if macd:
        crossover = macd.get("crossover", "")
        if "Bullish" in crossover:
            bullish += 1
        elif "Bearish" in crossover:
            bearish += 1

    if ma_str:
        if "Golden" in ma_str:
            bullish += 1
        elif "Death" in ma_str:
            bearish += 1

    if bullish >= 2:
        return "🟢 Bullish"
    if bearish >= 2:
        return "🔴 Bearish"
    return "⚪ Neutral"


# ── Markdown summary table ────────────────────────────────────────────────────

def format_indicator_table(
    ticker: str,
    current_price: float,
    rsi: Optional[float],
    macd: Optional[Dict],
    ma_str: Optional[str],
    bb: Optional[Dict] = None,
) -> str:
    """Render a Markdown indicator table for a single ticker."""
    rows = [
        ("Current Price",    f"${current_price:.2f}"),
        ("RSI",              f"{rsi:.1f}  {rsi_signal(rsi)}" if rsi else "N/A"),
        ("MACD Signal",      macd_signal(macd)),
        ("MA Cross",         ma_signal(ma_str)),
        ("Bollinger Bands",  bollinger_signal(bb, current_price)),
        ("Overall Signal",   overall_signal(rsi, macd, ma_str)),
    ]
    header = (
        f"### 📉 Technical Indicators — {ticker}\n\n"
        "| Indicator | Signal |\n"
        "|-----------|--------|"
    )
    lines = [header] + [f"| {k} | {v} |" for k, v in rows]
    return "\n".join(lines)


def format_multi_indicator_table(entries: List[Dict[str, Any]]) -> str:
    """
    Render a side-by-side Markdown indicator table for multiple tickers.

    Each entry: {"ticker", "current_price", "rsi", "macd", "ma_signal", "bb"}
    """
    if not entries:
        return "_No indicator data._"

    tickers = [e.get("ticker", "—") for e in entries]
    header = "| Indicator | " + " | ".join(tickers) + " |\n"
    sep    = "|-----------|" + "-----------|" * len(tickers)

    def row(label: str, fn, *keys) -> str:
        vals = []
        for e in entries:
            try:
                args = [e.get(k) for k in keys]
                vals.append(str(fn(*args)))
            except Exception:
                vals.append("N/A")
        return f"| {label} | " + " | ".join(vals) + " |"

    price_row = "| Price | " + " | ".join(
        f"${e.get('current_price', 0):.2f}" for e in entries
    ) + " |"

    rsi_row   = row("RSI Signal",   rsi_signal,      "rsi")
    macd_row  = row("MACD",         macd_signal,     "macd")
    ma_row    = row("MA Cross",     ma_signal,       "ma_signal")
    over_row  = "| Overall | " + " | ".join(
        overall_signal(e.get("rsi"), e.get("macd"), e.get("ma_signal"))
        for e in entries
    ) + " |"

    return (
        f"### 📉 Indicator Comparison\n\n"
        f"{header}{sep}\n"
        f"{price_row}\n{rsi_row}\n{macd_row}\n{ma_row}\n{over_row}"
    )
