"""
Volume Indicators Module for MarketPulse.
Provides On-Balance Volume (OBV), Accumulation/Distribution Line (ADL),
and Chaikin Money Flow (CMF) indicators.
"""

from typing import Any, Dict, List


def compute_obv(price_history: List[Dict[str, Any]]) -> List[float]:
    """
    Compute On-Balance Volume (OBV) series.

    Args:
        price_history: List of OHLCV dicts, sorted oldest-first.
                       Expects 'close'/'Close' and 'volume'/'Volume'.

    Returns:
        List of OBV values, same length as price_history.
    """
    if not price_history:
        return []

    obv_series = []
    current_obv = 0.0

    for i, bar in enumerate(price_history):
        close = bar.get("close") or bar.get("Close")
        volume = bar.get("volume") or bar.get("Volume")

        try:
            close_val = float(close) if close is not None else 0.0
            volume_val = float(volume) if volume is not None else 0.0
        except (ValueError, TypeError):
            close_val = 0.0
            volume_val = 0.0

        if i == 0:
            current_obv = volume_val
        else:
            prev_bar = price_history[i - 1]
            prev_close = prev_bar.get("close") or prev_bar.get("Close")
            try:
                prev_close_val = float(prev_close) if prev_close is not None else 0.0
            except (ValueError, TypeError):
                prev_close_val = 0.0

            if close_val > prev_close_val:
                current_obv += volume_val
            elif close_val < prev_close_val:
                current_obv -= volume_val

        obv_series.append(round(current_obv, 2))

    return obv_series
