"""
Unit tests for roic_calculator, dividend_projector, and split_adjuster tools.
"""

from tools.dividend_projector import project_dividend_yield_on_cost
from tools.roic_calculator import calculate_roic_efficiency
from tools.split_adjuster import adjust_position_for_stock_split


def test_calculate_roic_efficiency():
    res = calculate_roic_efficiency(nopat=50.0, total_debt=200.0, total_equity=300.0, cash=50.0)
    assert res["roic_pct"] == 11.11
    assert "capital_allocation_rating" in res


def test_project_dividend_yield_on_cost():
    res = project_dividend_yield_on_cost(initial_investment=1000.0, current_dividend_yield_pct=4.0, annual_dividend_growth_rate_pct=10.0, years=5)
    assert len(res["timeline"]) == 5
    assert res["final_year_yoc_pct"] > 4.0


def test_adjust_position_for_stock_split():
    res = adjust_position_for_stock_split(shares=10.0, avg_cost=100.0, split_ratio_numerator=10, split_ratio_denominator=1)
    assert res["adjusted_shares"] == 100.0
    assert res["adjusted_avg_cost"] == 10.0
