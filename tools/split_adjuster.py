"""
MarketPulse — Stock Split & Reverse Split Price Adjustment Normalizer
Adjusts share count, cost basis, and price history series for corporate stock splits.
"""

from typing import Any, Dict, List


def adjust_position_for_stock_split(
    shares: float,
    avg_cost: float,
    split_ratio_numerator: int = 10,
    split_ratio_denominator: int = 1,
) -> Dict[str, Any]:
    """
    Adjusts share count and average purchase cost after stock split.
    Example: 10-for-1 split -> numerator=10, denominator=1.
    """
    if shares <= 0 or avg_cost <= 0 or split_ratio_numerator <= 0 or split_ratio_denominator <= 0:
        return {"adjusted_shares": shares, "adjusted_avg_cost": avg_cost}

    multiplier = split_ratio_numerator / split_ratio_denominator
    new_shares = round(shares * multiplier, 4)
    new_cost = round(avg_cost / multiplier, 4)

    return {
        "original_shares": shares,
        "original_avg_cost": avg_cost,
        "split_ratio": f"{split_ratio_numerator}:{split_ratio_denominator}",
        "adjusted_shares": new_shares,
        "adjusted_avg_cost": new_cost,
    }
