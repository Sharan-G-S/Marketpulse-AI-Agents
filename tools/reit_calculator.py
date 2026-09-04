"""
MarketPulse — Real Estate REIT Dividend Yield & Cap Rate Valuation Calculator
Computes REIT Capitalization Rate (Cap Rate), FFO per share, and price-to-FFO multiple.
"""

from typing import Any, Dict


def calculate_reit_valuation(
    share_price: float,
    net_operating_income: float,
    property_value: float,
    ffo_per_share: float,
    dividend_per_share: float,
) -> Dict[str, Any]:
    """
    Computes REIT Cap Rate percentage, Price-to-FFO, and Dividend Yield.
    """
    if property_value <= 0 or share_price <= 0 or ffo_per_share <= 0:
        return {"cap_rate_pct": 0.0, "p_ffo_multiple": 0.0, "dividend_yield_pct": 0.0}

    cap_rate = round((net_operating_income / property_value) * 100.0, 2)
    p_ffo = round(share_price / ffo_per_share, 2)
    div_yield = round((dividend_per_share / share_price) * 100.0, 2)

    status = "Attractive Valuation (Low P/FFO & High Cap Rate)" if p_ffo < 15.0 and cap_rate >= 6.0 else "Standard Valuation"

    return {
        "share_price": share_price,
        "cap_rate_pct": cap_rate,
        "p_ffo_multiple": p_ffo,
        "dividend_yield_pct": div_yield,
        "valuation_status": status,
    }
