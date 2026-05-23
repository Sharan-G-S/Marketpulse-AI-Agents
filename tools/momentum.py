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
