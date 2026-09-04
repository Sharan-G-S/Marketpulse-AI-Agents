"""
MarketPulse — Dividend Growth Rate & Compound Yield-on-Cost Projection Tool
Projects 10-year compounding dividend income growth and Yield-on-Cost (YoC).
"""

from typing import Any, Dict, List


def project_dividend_yield_on_cost(
    initial_investment: float,
    current_dividend_yield_pct: float,
    annual_dividend_growth_rate_pct: float = 7.0,
    years: int = 10,
) -> Dict[str, Any]:
    """
    Computes compounding dividend income and Yield-on-Cost over time horizon.
    """
    if initial_investment <= 0 or years <= 0:
        return {"error": "Invalid inputs for dividend projection."}

    yoc_timeline: List[Dict[str, Any]] = []
    current_div_pct = current_dividend_yield_pct
    annual_income = initial_investment * (current_div_pct / 100.0)

    for yr in range(1, years + 1):
        if yr > 1:
            annual_income *= (1.0 + annual_dividend_growth_rate_pct / 100.0)
            current_div_pct = (annual_income / initial_investment) * 100.0

        yoc_timeline.append({
            "year": yr,
            "annual_dividend_income": round(float(annual_income), 2),
            "yield_on_cost_pct": round(float(current_div_pct), 2),
        })

    return {
        "initial_investment": initial_investment,
        "starting_yield_pct": current_dividend_yield_pct,
        "growth_rate_pct": annual_dividend_growth_rate_pct,
        "final_year_yoc_pct": yoc_timeline[-1]["yield_on_cost_pct"],
        "timeline": yoc_timeline,
    }
