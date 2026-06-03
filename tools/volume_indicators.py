"""
Volume Indicators Module for MarketPulse.
Provides On-Balance Volume (OBV), Accumulation/Distribution Line (ADL),
and Chaikin Money Flow (CMF) indicators.
"""

from typing import Any, Dict, List, Optional


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


def compute_adl(price_history: List[Dict[str, Any]]) -> List[float]:
    """
    Compute Accumulation/Distribution Line (ADL) series.

    Args:
        price_history: List of OHLCV dicts, sorted oldest-first.

    Returns:
        List of ADL values, same length as price_history.
    """
    if not price_history:
        return []

    adl_series = []
    current_adl = 0.0

    for bar in price_history:
        close = bar.get("close") or bar.get("Close")
        high = bar.get("high") or bar.get("High")
        low = bar.get("low") or bar.get("Low")
        volume = bar.get("volume") or bar.get("Volume")

        try:
            close_val = float(close) if close is not None else 0.0
            high_val = float(high) if high is not None else 0.0
            low_val = float(low) if low is not None else 0.0
            vol_val = float(volume) if volume is not None else 0.0
        except (ValueError, TypeError):
            close_val = 0.0
            high_val = 0.0
            low_val = 0.0
            vol_val = 0.0

        if high_val - low_val == 0.0:
            mfm = 0.0
        else:
            mfm = ((close_val - low_val) - (high_val - close_val)) / (high_val - low_val)

        mfv = mfm * vol_val
        current_adl += mfv
        adl_series.append(round(current_adl, 2))

    return adl_series


def compute_cmf(price_history: List[Dict[str, Any]], period: int = 20) -> List[Optional[float]]:
    """
    Compute Chaikin Money Flow (CMF) series.

    Args:
        price_history: List of OHLCV dicts, sorted oldest-first.
        period: CMF period (default 20).

    Returns:
        List of CMF values (or None for initial window), same length as price_history.
    """
    if not price_history:
        return []

    if period <= 0:
        return [None] * len(price_history)

    mfv_list = []
    vol_list = []

    for bar in price_history:
        close = bar.get("close") or bar.get("Close")
        high = bar.get("high") or bar.get("High")
        low = bar.get("low") or bar.get("Low")
        volume = bar.get("volume") or bar.get("Volume")

        try:
            close_val = float(close) if close is not None else 0.0
            high_val = float(high) if high is not None else 0.0
            low_val = float(low) if low is not None else 0.0
            vol_val = float(volume) if volume is not None else 0.0
        except (ValueError, TypeError):
            close_val = 0.0
            high_val = 0.0
            low_val = 0.0
            vol_val = 0.0

        if high_val - low_val == 0.0:
            mfm = 0.0
        else:
            mfm = ((close_val - low_val) - (high_val - close_val)) / (high_val - low_val)

        mfv_list.append(mfm * vol_val)
        vol_list.append(vol_val)

    cmf_series = []
    for i in range(len(price_history)):
        if i + 1 < period:
            cmf_series.append(None)
        else:
            sum_mfv = sum(mfv_list[i + 1 - period : i + 1])
            sum_vol = sum(vol_list[i + 1 - period : i + 1])
            if sum_vol == 0.0:
                cmf_series.append(0.0)
            else:
                cmf_series.append(round(sum_mfv / sum_vol, 4))

    return cmf_series
