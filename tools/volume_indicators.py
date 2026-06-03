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


def generate_volume_signals(price_history: List[Dict[str, Any]]) -> Dict[str, Any]:  # noqa: C901
    """
    Generate trend signals based on On-Balance Volume (OBV),
    Accumulation/Distribution Line (ADL), and Chaikin Money Flow (CMF).

    Args:
        price_history: List of OHLCV dicts, sorted oldest-first.

    Returns:
        Dict with current values, trends, signals, and interpretation.
    """
    if len(price_history) < 2:
        return {
            "obv": None,
            "adl": None,
            "cmf": None,
            "obv_trend": "Neutral",
            "adl_trend": "Neutral",
            "cmf_signal": "Neutral",
            "composite_signal": "Insufficient Data",
            "interpretation": "Insufficient history to analyze volume trends.",
        }

    obv_series = compute_obv(price_history)
    adl_series = compute_adl(price_history)
    cmf_series = compute_cmf(price_history, period=min(20, len(price_history)))

    last_obv = obv_series[-1]
    last_adl = adl_series[-1]
    last_cmf = cmf_series[-1]

    # Trend calculation lookback window (up to 5 bars)
    lookback = min(5, len(price_history) - 1)
    prev_obv = obv_series[-1 - lookback]
    prev_adl = adl_series[-1 - lookback]

    # OBV trend
    if last_obv > prev_obv:
        obv_trend = "Bullish Accumulation"
    elif last_obv < prev_obv:
        obv_trend = "Bearish Distribution"
    else:
        obv_trend = "Flat"

    # ADL trend
    if last_adl > prev_adl:
        adl_trend = "Bullish Accumulation"
    elif last_adl < prev_adl:
        adl_trend = "Bearish Distribution"
    else:
        adl_trend = "Flat"

    # CMF Signal
    if last_cmf is not None:
        if last_cmf > 0.05:
            cmf_signal = "Bullish"
        elif last_cmf < -0.05:
            cmf_signal = "Bearish"
        else:
            cmf_signal = "Neutral"
    else:
        cmf_signal = "Neutral"

    # Composite signal
    bullish_votes = 0
    bearish_votes = 0

    if "Bullish" in obv_trend:
        bullish_votes += 1
    elif "Bearish" in obv_trend:
        bearish_votes += 1

    if "Bullish" in adl_trend:
        bullish_votes += 1
    elif "Bearish" in adl_trend:
        bearish_votes += 1

    if cmf_signal == "Bullish":
        bullish_votes += 1
    elif cmf_signal == "Bearish":
        bearish_votes += 1

    if bullish_votes >= 2:
        composite = "Bullish"
        interpretation = (
            f"Strong buying pressure detected across volume indicators. "
            f"CMF at {last_cmf if last_cmf is not None else 0:.4f} and rising trends "
            f"in OBV/ADL support an upward price continuation."
        )
    elif bearish_votes >= 2:
        composite = "Bearish"
        interpretation = (
            f"Selling pressure and distribution detected across volume indicators. "
            f"CMF at {last_cmf if last_cmf is not None else 0:.4f} and declining trends "
            f"in OBV/ADL indicate institutional distribution."
        )
    else:
        composite = "Neutral"
        interpretation = "Volume indicators show conflicting or flat momentum. The trend is range-bound."

    return {
        "obv": last_obv,
        "adl": last_adl,
        "cmf": last_cmf,
        "obv_trend": obv_trend,
        "adl_trend": adl_trend,
        "cmf_signal": cmf_signal,
        "composite_signal": composite,
        "interpretation": interpretation,
    }


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_obv",
    "compute_adl",
    "compute_cmf",
    "generate_volume_signals",
]

_MODULE = "tools/volume_indicators"
_VERSION = "2.0.0"
