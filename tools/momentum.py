"""
Momentum Indicators Module
Provides Williams %R, CCI, and Rate of Change (ROC) indicators.
"""

from typing import Any, Dict, List


def compute_williams_r(price_history: List[Dict], period: int = 14) -> Dict[str, Any]:
    """Compute Williams %R momentum oscillator.

    Williams %R = (Highest High - Close) / (Highest High - Lowest Low) * -100
    Values range from -100 to 0. Below -80 is oversold, above -20 is overbought.
    """
    if len(price_history) < period:
        return {"value": None, "signal": "Insufficient data", "zone": "N/A"}

    window = price_history[-period:]
    highest_high = max(r.get("high", r.get("close", 0)) for r in window)
    lowest_low = min(r.get("low", r.get("close", 0)) for r in window)
    close = price_history[-1].get("close", 0)

    denom = highest_high - lowest_low
    if denom == 0:
        value = -50.0
    else:
        value = round((highest_high - close) / denom * -100, 2)

    if value >= -20:
        zone = "Overbought"
    elif value <= -80:
        zone = "Oversold"
    else:
        zone = "Neutral"

    signal = "Bearish" if zone == "Overbought" else "Bullish" if zone == "Oversold" else "Neutral"
    return {"value": value, "signal": signal, "zone": zone}


def compute_cci(price_history: List[Dict], period: int = 20) -> Dict[str, Any]:
    """Compute Commodity Channel Index (CCI).

    CCI = (Typical Price - SMA of Typical Price) / (0.015 * Mean Deviation)
    Above +100 is overbought, below -100 is oversold.
    """
    if len(price_history) < period:
        return {"value": None, "signal": "Insufficient data", "zone": "N/A"}

    window = price_history[-period:]
    typical_prices = [
        (r.get("high", r.get("close", 0)) + r.get("low", r.get("close", 0)) + r.get("close", 0)) / 3
        for r in window
    ]
    sma = sum(typical_prices) / period
    mean_dev = sum(abs(tp - sma) for tp in typical_prices) / period

    if mean_dev == 0:
        cci_val = 0.0
    else:
        cci_val = round((typical_prices[-1] - sma) / (0.015 * mean_dev), 2)

    if cci_val > 100:
        zone = "Overbought"
    elif cci_val < -100:
        zone = "Oversold"
    else:
        zone = "Neutral"

    signal = "Bearish" if zone == "Overbought" else "Bullish" if zone == "Oversold" else "Neutral"
    return {"value": cci_val, "signal": signal, "zone": zone}


def compute_roc(closes: List[float], period: int = 10) -> Dict[str, Any]:
    """Compute Rate of Change (ROC).

    ROC = (Close - Close[n periods ago]) / Close[n periods ago] * 100
    Positive ROC = bullish momentum, negative = bearish.
    """
    if len(closes) < period + 1:
        return {"value": None, "signal": "Insufficient data", "pct_change": None}

    prev_close = closes[-(period + 1)]
    if prev_close == 0:
        return {"value": None, "signal": "Division by zero", "pct_change": None}

    roc_val = round((closes[-1] - prev_close) / prev_close * 100, 2)
    signal = "Bullish" if roc_val > 0 else "Bearish" if roc_val < 0 else "Neutral"
    return {"value": roc_val, "signal": signal, "pct_change": f"{roc_val:+.2f}%"}
