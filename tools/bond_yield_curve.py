"""
MarketPulse — Bond Yield Curve & Interest Rate Sensitivity Duration Calculator
Computes fixed-income bond yield to maturity (YTM), Macaulay duration, and price sensitivity.
"""

from typing import Any, Dict


def calculate_bond_metrics(
    face_value: float = 1000.0,
    coupon_rate_pct: float = 5.0,
    years_to_maturity: int = 10,
    current_bond_price: float = 950.0,
) -> Dict[str, Any]:
    """
    Calculates bond Yield to Maturity (YTM) and Macaulay duration.
    """
    if face_value <= 0 or current_bond_price <= 0 or years_to_maturity <= 0:
        return {"ytm_pct": 0.0, "macaulay_duration_years": 0.0}

    coupon = face_value * (coupon_rate_pct / 100.0)
    ytm = (coupon + (face_value - current_bond_price) / years_to_maturity) / ((face_value + current_bond_price) / 2.0)
    ytm_pct = round(float(ytm * 100.0), 2)

    # Approximate Macaulay Duration
    duration = (1.0 + ytm) / ytm - (1.0 + ytm + years_to_maturity * (coupon_rate_pct / 100.0 - ytm)) / (ytm + (coupon_rate_pct / 100.0) * ((1.0 + ytm)**years_to_maturity - 1.0))
    duration_years = round(abs(float(duration)), 2)

    return {
        "face_value": face_value,
        "current_bond_price": current_bond_price,
        "coupon_rate_pct": coupon_rate_pct,
        "years_to_maturity": years_to_maturity,
        "ytm_pct": ytm_pct,
        "macaulay_duration_years": duration_years,
        "sensitivity_per_100bp": f"{duration_years:.2f}% price change per 1% rate shift",
    }
