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
    """Compute Commodity Channel Index (CCI)."""
    pass
