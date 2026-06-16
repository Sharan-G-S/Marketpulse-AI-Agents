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


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_support_resistance",
]

_MODULE = "tools/price_targets"
_VERSION = "2.1.0"
