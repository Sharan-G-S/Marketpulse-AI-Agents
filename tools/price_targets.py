"""
Price Target & Support/Resistance Module for MarketPulse.

Computes classical pivot-point support/resistance levels,
ATR-based price targets (bull/bear/neutral), and Markdown report formatting.

No LLM required — pure price analysis.
"""

from typing import Any, Dict, List, Optional

# ── Support & Resistance via Pivot Points ─────────────────────────────────────


def compute_support_resistance(
    price_history: List[Dict[str, Any]],
    n_periods: int = 5,
) -> Dict[str, Optional[float]]:
    """
    Compute classic pivot-point support and resistance levels from recent bars.

    Uses the standard pivot-point formula based on the prior period's
    High, Low, and Close prices:
        Pivot  = (High + Low + Close) / 3
        R1     = 2 × Pivot − Low
        R2     = Pivot + (High − Low)
        S1     = 2 × Pivot − High
        S2     = Pivot − (High − Low)

    Args:
        price_history: OHLCV list sorted oldest-first.
        n_periods:     Number of recent bars to average for the base H/L/C
                       calculation (default 5).

    Returns:
        Dict with keys: pivot, r1, r2, s1, s2 (all floats or None).
    """
    if not price_history or len(price_history) < 2:
        return {"pivot": None, "r1": None, "r2": None, "s1": None, "s2": None}

    window = price_history[-min(n_periods, len(price_history)):]

    try:
        highs = [r.get("high") or r.get("close", 0) for r in window]
        lows = [r.get("low") or r.get("close", 0) for r in window]
        closes = [r.get("close", 0) for r in window]

        high = max(highs)
        low = min(lows)
        close = closes[-1]

        if high == 0 and low == 0:
            return {"pivot": None, "r1": None, "r2": None, "s1": None, "s2": None}

        pivot = round((high + low + close) / 3, 4)
        r1 = round(2 * pivot - low, 4)
        r2 = round(pivot + (high - low), 4)
        s1 = round(2 * pivot - high, 4)
        s2 = round(pivot - (high - low), 4)

        return {"pivot": pivot, "r1": r1, "r2": r2, "s1": s1, "s2": s2}
    except (TypeError, ValueError, KeyError):
        return {"pivot": None, "r1": None, "r2": None, "s1": None, "s2": None}


# ── ATR-based Price Targets ───────────────────────────────────────────────────


def compute_price_target(
    price_history: List[Dict[str, Any]],
    atr_multiplier: float = 1.5,
) -> Dict[str, Any]:
    """
    Compute ATR-based bullish, bearish, and neutral price targets.

    Uses the Average True Range (ATR) over the last min(14, n) bars to
    project upside and downside price targets from the most recent close.

        Bull target  = last_close + atr_multiplier × ATR
        Bear target  = last_close − atr_multiplier × ATR
        Neutral zone = [Bear target, Bull target]

    Args:
        price_history:   OHLCV list sorted oldest-first.
        atr_multiplier:  Scaling factor applied to ATR (default 1.5).

    Returns:
        Dict with keys: current_price, atr, bull_target, bear_target,
        target_range_pct, and bias (str).
    """
    if len(price_history) < 2:
        return {
            "current_price": None,
            "atr": None,
            "bull_target": None,
            "bear_target": None,
            "target_range_pct": None,
            "bias": "Insufficient Data",
        }

    try:
        period = min(14, len(price_history) - 1)
        recent = price_history[-(period + 1):]

        true_ranges: List[float] = []
        for i in range(1, len(recent)):
            high = recent[i].get("high") or recent[i].get("close", 0)
            low = recent[i].get("low") or recent[i].get("close", 0)
            prev_close = recent[i - 1].get("close", 0)
            tr = max(
                abs(high - low),
                abs(high - prev_close),
                abs(low - prev_close),
            )
            true_ranges.append(tr)

        if not true_ranges:
            atr = 0.0
        else:
            atr = round(sum(true_ranges) / len(true_ranges), 4)

        current_price = price_history[-1].get("close", 0)
        if not current_price:
            raise ValueError("Zero or missing close price")

        bull_target = round(current_price + atr_multiplier * atr, 4)
        bear_target = round(current_price - atr_multiplier * atr, 4)
        target_range_pct = round(
            (bull_target - bear_target) / current_price * 100, 2
        ) if current_price else None

        # Simple bias from recent price trend
        first_close = price_history[0].get("close", current_price)
        bias = "Bullish" if current_price > first_close else (
            "Bearish" if current_price < first_close else "Neutral"
        )

        return {
            "current_price": current_price,
            "atr": atr,
            "bull_target": bull_target,
            "bear_target": bear_target,
            "target_range_pct": target_range_pct,
            "bias": bias,
        }
    except (TypeError, ValueError, KeyError):
        return {
            "current_price": None,
            "atr": None,
            "bull_target": None,
            "bear_target": None,
            "target_range_pct": None,
            "bias": "Error",
        }


# ── Markdown Report ───────────────────────────────────────────────────────────


def format_price_target_report(
    ticker: str,
    price_target: Dict[str, Any],
    support_resistance: Dict[str, Any],
) -> str:
    """
    Render a Markdown price target and support/resistance report for one ticker.

    Args:
        ticker:             Ticker symbol.
        price_target:       Output of ``compute_price_target()``.
        support_resistance: Output of ``compute_support_resistance()``.

    Returns:
        Markdown-formatted string with price targets and S/R levels.
    """
    bias = price_target.get("bias", "N/A")
    bias_emoji = "🟢" if bias == "Bullish" else ("🔴" if bias == "Bearish" else "⚪")
    cp = price_target.get("current_price")
    cp_str = f"${cp:.2f}" if cp is not None else "N/A"
    atr = price_target.get("atr")
    atr_str = f"${atr:.4f}" if atr is not None else "N/A"
    bull = price_target.get("bull_target")
    bear = price_target.get("bear_target")
    bull_str = f"${bull:.2f}" if bull is not None else "N/A"
    bear_str = f"${bear:.2f}" if bear is not None else "N/A"
    rng = price_target.get("target_range_pct")
    rng_str = f"{rng:.2f}%" if rng is not None else "N/A"

    pivot = support_resistance.get("pivot")
    r1 = support_resistance.get("r1")
    r2 = support_resistance.get("r2")
    s1 = support_resistance.get("s1")
    s2 = support_resistance.get("s2")

    def _fmt(v: Optional[float]) -> str:
        return f"${v:.2f}" if v is not None else "N/A"

    lines = [
        f"### 🎯 Price Targets — {ticker}",
        "",
        f"**Bias:** {bias_emoji} {bias}  |  **Current Price:** {cp_str}",
        f"**ATR:** {atr_str}  |  **Target Range:** {rng_str}",
        "",
        "| Level | Price |",
        "|-------|-------|",
        f"| 🟢 Bull Target (R) | {bull_str} |",
        f"| 🔵 Pivot | {_fmt(pivot)} |",
        f"| 🔴 Bear Target (S) | {bear_str} |",
        "",
        "#### Support & Resistance Levels",
        "",
        "| Level | Price |",
        "|-------|-------|",
        f"| R2 (Strong Resistance) | {_fmt(r2)} |",
        f"| R1 (Resistance) | {_fmt(r1)} |",
        f"| Pivot | {_fmt(pivot)} |",
        f"| S1 (Support) | {_fmt(s1)} |",
        f"| S2 (Strong Support) | {_fmt(s2)} |",
    ]
    return "\n".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_support_resistance",
    "compute_price_target",
    "format_price_target_report",
]

_MODULE = "tools/price_targets"
_VERSION = "2.1.0"
