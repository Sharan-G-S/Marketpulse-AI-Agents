"""
Regression test suite verifying ZeroDivision, NaN, and short-history edge cases.
"""

from tools.indicators import compute_rsi
from tools.portfolio_performance import compute_position, compute_portfolio
from tools.risk_metrics import max_drawdown, sharpe_ratio
from tools.stock_tools import calculate_price_change


def test_calculate_price_change_zero_start():
    data = [{"close": 0.0}, {"close": 150.0}]
    res = calculate_price_change.invoke({"price_history": data})
    assert res["change_pct"] == 0.0
    assert "error" not in res


def test_compute_position_none_values():
    pos = {"ticker": "AAPL", "qty": None, "avg_cost": None}
    res = compute_position(pos, current_price=150.0)
    assert res["qty"] == 0.0
    assert res["cost_basis"] == 0.0
    assert res["unrealised_pct"] is None


def test_max_drawdown_zero_peak():
    data = [{"close": 0.0}, {"close": 10.0}]
    mdd = max_drawdown(data)
    assert mdd == 0.0


def test_sharpe_ratio_flat_returns():
    rets = [0.01, 0.01, 0.01]
    sr = sharpe_ratio(rets)
    assert sr == 0.0


def test_compute_rsi_flat_prices():
    closes = [100.0] * 20
    rsi = compute_rsi(closes)
    assert rsi in [50.0, 100.0]
