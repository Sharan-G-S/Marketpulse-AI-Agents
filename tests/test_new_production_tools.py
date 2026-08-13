"""
Unit tests for new production tools (fair_value_calculator, beta_hedger, liquidity_risk).
"""

from tools.beta_hedger import calculate_beta_hedge
from tools.fair_value_calculator import calculate_intrinsic_fair_value
from tools.liquidity_risk import estimate_liquidity_slippage


def test_calculate_intrinsic_fair_value():
    res = calculate_intrinsic_fair_value(current_price=100.0, eps=5.0)
    assert res["current_price"] == 100.0
    assert res["fair_value_estimate"] > 0
    assert "valuation_status" in res


def test_calculate_beta_hedge():
    res = calculate_beta_hedge(portfolio_value=100000.0, portfolio_beta=1.2, index_price=500.0)
    assert res["hedge_value_required"] == 120000.0
    assert res["index_shares_to_short"] == 240.0


def test_estimate_liquidity_slippage():
    res = estimate_liquidity_slippage(order_size_shares=50000, avg_daily_volume=1000000)
    assert res["participation_rate_pct"] == 5.0
    assert res["estimated_slippage_pct"] > 0
