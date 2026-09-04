"""
Unit tests for options_pricing, bond_yield_curve, and reit_calculator tools.
"""

from tools.bond_yield_curve import calculate_bond_metrics
from tools.options_pricing import calculate_black_scholes
from tools.reit_calculator import calculate_reit_valuation


def test_calculate_black_scholes():
    res = calculate_black_scholes(stock_price=100.0, strike_price=100.0)
    assert res["call_price"] > 0
    assert res["put_price"] > 0
    assert 0.0 <= res["call_delta"] <= 1.0


def test_calculate_bond_metrics():
    res = calculate_bond_metrics(face_value=1000.0, current_bond_price=950.0)
    assert res["ytm_pct"] > 5.0
    assert res["macaulay_duration_years"] > 0


def test_calculate_reit_valuation():
    res = calculate_reit_valuation(share_price=50.0, net_operating_income=10.0, property_value=100.0, ffo_per_share=4.0, dividend_per_share=2.5)
    assert res["cap_rate_pct"] == 10.0
    assert res["p_ffo_multiple"] == 12.5
