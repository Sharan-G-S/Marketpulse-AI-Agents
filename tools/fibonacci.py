from typing import Dict, List


def calculate_fibonacci_levels(price_history: List[Dict]) -> Dict[str, float]:
    """Calculate Fibonacci retracement levels for a given price history."""
    if not price_history:
        return {}
    highs = [r.get("high", r.get("close", 0)) for r in price_history]
    lows = [r.get("low", r.get("close", 0)) for r in price_history]
    max_high = max(highs)
    min_low = min(lows)
    diff = max_high - min_low
    levels: Dict[str, float] = {}
    levels["0.236"] = round(max_high - 0.236 * diff, 2)
    levels["0.382"] = round(max_high - 0.382 * diff, 2)
    levels["0.500"] = round(max_high - 0.500 * diff, 2)
    pass
