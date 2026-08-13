"""
MarketPulse — Intrinsic Fair Value Calculator
Estimates intrinsic share value using Gordon Growth Dividend Discount Model (DDM) & DCF.
"""

from typing import Any, Dict


def calculate_intrinsic_fair_value(
    current_price: float,
    eps: float,
    growth_rate: float = 0.08,
    discount_rate: float = 0.10,
    terminal_multiple: float = 15.0,
) -> Dict[str, Any]:
    """
    Computes intrinsic fair value estimate using 5-year discounted earnings model.

    Args:
        current_price: Current market price per share
        eps: Trailing 12-month Earnings Per Share
        growth_rate: Projected annual EPS growth rate (decimal)
        discount_rate: Required discount rate (decimal)
        terminal_multiple: Exit PE multiple

    Returns:
        Dict with fair_value_estimate, margin_of_safety_pct, and valuation_status.
    """
    if not current_price or current_price <= 0 or not eps or eps <= 0:
        return {
            "current_price": current_price,
            "fair_value_estimate": current_price,
            "margin_of_safety_pct": 0.0,
            "valuation_status": "Neutral / Fairly Valued",
        }

    # 5-year projected discounted earnings
    discounted_cash_flows = 0.0
    future_eps = eps

    for year in range(1, 6):
        future_eps *= (1 + growth_rate)
        discounted_cash_flows += future_eps / ((1 + discount_rate) ** year)

    terminal_value = (future_eps * terminal_multiple) / ((1 + discount_rate) ** 5)
    fair_value = round(float(discounted_cash_flows + terminal_value), 2)

    mos_pct = round(((fair_value - current_price) / fair_value) * 100.0 if fair_value else 0.0, 2)

    if mos_pct >= 20.0:
        status = "Undervalued (Strong Margin of Safety)"
    elif mos_pct <= -20.0:
        status = "Overvalued (Premium Pricing)"
    else:
        status = "Fairly Valued"

    return {
        "current_price": current_price,
        "fair_value_estimate": fair_value,
        "margin_of_safety_pct": mos_pct,
        "valuation_status": status,
    }
