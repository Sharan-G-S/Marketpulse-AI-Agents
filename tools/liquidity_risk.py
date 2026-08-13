"""
MarketPulse — Liquidity Risk & Execution Slippage Impact Model
Estimates market impact cost and execution slippage percentage for large institutional orders.
"""

from typing import Any, Dict


def estimate_liquidity_slippage(
    order_size_shares: int,
    avg_daily_volume: int,
    volatility_pct: float = 0.02,
) -> Dict[str, Any]:
    """
    Estimates market impact slippage using Square-Root Law of Market Impact.

    Slippage % ≈ volatility * sqrt(order_size / ADV)

    Args:
        order_size_shares: Number of shares in proposed order
        avg_daily_volume: Average Daily Volume (ADV)
        volatility_pct: Daily asset return volatility (decimal)

    Returns:
        Dict with estimated_slippage_pct, impact_tier, and participation_rate_pct.
    """
    if not avg_daily_volume or avg_daily_volume <= 0 or not order_size_shares or order_size_shares <= 0:
        return {"estimated_slippage_pct": 0.0, "impact_tier": "Low Impact", "participation_rate_pct": 0.0}

    participation_rate = (order_size_shares / avg_daily_volume) * 100.0
    vol = max(0.005, volatility_pct)

    import math
    slippage_pct = round(float(vol * math.sqrt(order_size_shares / avg_daily_volume) * 100.0), 3)

    if participation_rate >= 10.0:
        tier = "High Liquidity Impact (Heavy Slippage)"
    elif participation_rate >= 2.0:
        tier = "Moderate Liquidity Impact"
    else:
        tier = "Low Liquidity Impact (Negligible Slippage)"

    return {
        "order_size_shares": order_size_shares,
        "avg_daily_volume": avg_daily_volume,
        "participation_rate_pct": round(participation_rate, 2),
        "estimated_slippage_pct": slippage_pct,
        "impact_tier": tier,
    }
