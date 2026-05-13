"""
Moving Average Crossover Signal Engine for MarketPulse.

Computes SMA and EMA series and detects Golden Cross / Death Cross
crossover events with signal history. No external dependencies — pure Python.
"""

from typing import Any, Dict, List, Optional, Tuple

# ── Moving average computation ────────────────────────────────────────────────

def compute_sma(prices: List[float], period: int) -> List[Optional[float]]:
    """
    Compute Simple Moving Average series.

    Args:
        prices: List of closing prices (oldest first).
        period: Look-back window in bars.

    Returns:
        List of SMA values, same length as prices.
        Values before the first full window are None.
    """
    result: List[Optional[float]] = []
    for i in range(len(prices)):
        if i + 1 < period:
            result.append(None)
        else:
            window = prices[i + 1 - period: i + 1]
            result.append(round(sum(window) / period, 6))
    return result


def compute_ema(prices: List[float], period: int) -> List[Optional[float]]:
    """
    Compute Exponential Moving Average series.

    Uses standard multiplier = 2 / (period + 1).

    Args:
        prices: List of closing prices (oldest first).
        period: EMA period.

    Returns:
        List of EMA values, same length as prices.
        Values before the first complete SMA seed are None.
    """
    if len(prices) < period:
        return [None] * len(prices)

    k = 2.0 / (period + 1)
    result: List[Optional[float]] = [None] * (period - 1)

    # Seed with first SMA
    seed = sum(prices[:period]) / period
    result.append(round(seed, 6))

    for price in prices[period:]:
        prev = result[-1]
        if prev is None:
            result.append(None)
        else:
            ema = round(price * k + prev * (1 - k), 6)
            result.append(ema)

    return result


# ── Crossover detection ───────────────────────────────────────────────────────

CrossoverEvent = Dict[str, Any]
"""
{
    "index":       int,     # bar index where crossover occurred
    "signal":      str,     # "Golden Cross" | "Death Cross"
    "fast_value":  float,
    "slow_value":  float,
}
"""


def detect_crossovers(
    fast_series: List[Optional[float]],
    slow_series: List[Optional[float]],
) -> List[CrossoverEvent]:
    """
    Detect Golden Cross and Death Cross events in two MA series.

    A Golden Cross occurs when fast MA crosses above slow MA.
    A Death Cross occurs when fast MA crosses below slow MA.

    Args:
        fast_series: Shorter-period MA series (e.g. SMA-50).
        slow_series: Longer-period MA series (e.g. SMA-200).

    Returns:
        List of CrossoverEvent dicts, in chronological order.
    """
    events: List[CrossoverEvent] = []
    n = min(len(fast_series), len(slow_series))

    for i in range(1, n):
        f_prev, f_curr = fast_series[i - 1], fast_series[i]
        s_prev, s_curr = slow_series[i - 1], slow_series[i]

        if any(v is None for v in (f_prev, f_curr, s_prev, s_curr)):
            continue

        was_below = f_prev < s_prev  # type: ignore[operator]
        now_above = f_curr > s_curr  # type: ignore[operator]
        was_above = f_prev > s_prev  # type: ignore[operator]
        now_below = f_curr < s_curr  # type: ignore[operator]

        if was_below and now_above:
            events.append({
                "index":      i,
                "signal":     "Golden Cross",
                "fast_value": f_curr,
                "slow_value": s_curr,
            })
        elif was_above and now_below:
            events.append({
                "index":      i,
                "signal":     "Death Cross",
                "fast_value": f_curr,
                "slow_value": s_curr,
            })

    return events


# ── Price-list extraction helper ──────────────────────────────────────────────

def extract_closes(price_history: List[Dict[str, Any]]) -> List[float]:
    """Extract closing prices from a price_history list (oldest first)."""
    closes = []
    for bar in price_history:
        c = bar.get("close") or bar.get("Close")
        if c is not None:
            try:
                closes.append(float(c))
            except (ValueError, TypeError):
                pass
    return closes


# ── Full signal summary ───────────────────────────────────────────────────────

def ma_crossover_summary(
    price_history: List[Dict[str, Any]],
    fast_period: int = 50,
    slow_period: int = 200,
    use_ema: bool = False,
) -> Dict[str, Any]:
    """
    Compute a complete MA crossover analysis for a price history.

    Args:
        price_history: List of OHLCV dicts, oldest first.
        fast_period:   Short MA period (default 50).
        slow_period:   Long MA period (default 200).
        use_ema:       If True, use EMA instead of SMA.

    Returns:
        Dict with current_signal, last_crossover, fast_value, slow_value,
        crossover_events, and ma_type.
    """
    closes = extract_closes(price_history)
    ma_type = "EMA" if use_ema else "SMA"
    if not closes:
        # Return a complete sentinel dict so callers don't hit KeyError on any
        # expected key (e.g. fast_value, slow_value, n_bars used in the UI).
        return {
            "ma_type":          ma_type,
            "fast_period":      fast_period,
            "slow_period":      slow_period,
            "fast_value":       None,
            "slow_value":       None,
            "current_signal":   "Insufficient Data",
            "last_crossover":   None,
            "crossover_events": [],
            "n_bars":           0,
        }

    ma_fn = compute_ema if use_ema else compute_sma

    fast_series = ma_fn(closes, fast_period)
    slow_series = ma_fn(closes, slow_period)

    events = detect_crossovers(fast_series, slow_series)

    # Current relationship
    f_last = next((v for v in reversed(fast_series) if v is not None), None)
    s_last = next((v for v in reversed(slow_series) if v is not None), None)

    if f_last is None or s_last is None:
        current = "Insufficient Data"
    elif f_last > s_last:
        current = f"Bullish ({ma_type}-{fast_period} above {ma_type}-{slow_period})"
    elif f_last < s_last:
        current = f"Bearish ({ma_type}-{fast_period} below {ma_type}-{slow_period})"
    else:
        current = "Neutral (MAs equal)"

    last_event = events[-1] if events else None

    return {
        "ma_type":          ma_type,
        "fast_period":      fast_period,
        "slow_period":      slow_period,
        "fast_value":       f_last,
        "slow_value":       s_last,
        "current_signal":   current,
        "last_crossover":   last_event,
        "crossover_events": events,
        "n_bars":           len(closes),
    }


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_sma",
    "compute_ema",
    "detect_crossovers",
    "extract_closes",
    "ma_crossover_summary",
]

_MODULE = "tools/ma_crossover.py"
_VERSION = "1.7.0"
