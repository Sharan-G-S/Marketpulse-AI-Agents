"""
MarketPulse — Altman Z-Score Financial Distress & Bankruptcy Model
Computes 5-ratio Altman Z-Score to assess corporate solvency health.
"""

from typing import Any, Dict


def calculate_altman_zscore(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_cap: float,
    total_revenue: float,
    total_assets: float,
    total_liabilities: float,
) -> Dict[str, Any]:
    """
    Computes Altman Z-Score: Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
    """
    if not total_assets or total_assets <= 0 or not total_liabilities or total_liabilities <= 0:
        return {"z_score": 0.0, "zone": "Distress Zone (High Solvency Risk)"}

    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = total_revenue / total_assets

    z = round(float(1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5), 2)

    if z >= 2.99:
        zone = "Safe Zone (Low Solvency Risk)"
    elif z >= 1.81:
        zone = "Grey Zone (Moderate Caution)"
    else:
        zone = "Distress Zone (High Solvency Risk)"

    return {
        "z_score": z,
        "zone": zone,
        "x1_working_capital_ratio": round(x1, 3),
        "x3_ebit_ratio": round(x3, 3),
        "x4_solvency_ratio": round(x4, 3),
    }
