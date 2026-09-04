"""
MarketPulse — Capital Allocation Efficiency (ROIC vs WACC) Calculator
Computes Return on Invested Capital (ROIC) and compares against cost of capital (WACC).
"""

from typing import Any, Dict


def calculate_roic_efficiency(
    nopat: float,
    total_debt: float,
    total_equity: float,
    cash: float,
    wacc_pct: float = 8.0,
) -> Dict[str, Any]:
    """
    Computes ROIC % = NOPAT / (Total Debt + Equity - Cash) and Economic Value Added (EVA) spread.
    """
    invested_capital = (total_debt + total_equity) - cash
    if invested_capital <= 0:
        return {"roic_pct": 0.0, "economic_spread_pct": 0.0, "rating": "N/A"}

    roic = round((nopat / invested_capital) * 100.0, 2)
    spread = round(roic - wacc_pct, 2)

    if spread >= 5.0:
        rating = "Exceptional Capital Allocator (Moat Business)"
    elif spread > 0.0:
        rating = "Value Creating Business"
    else:
        rating = "Value Destroying Business (ROIC < WACC)"

    return {
        "invested_capital": round(invested_capital, 2),
        "roic_pct": roic,
        "wacc_pct": wacc_pct,
        "economic_spread_pct": spread,
        "capital_allocation_rating": rating,
    }
