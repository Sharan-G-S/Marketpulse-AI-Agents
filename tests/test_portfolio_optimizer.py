"""
Unit tests for tools/portfolio_optimizer.py
"""

import numpy as np
from tools.portfolio_optimizer import optimize_portfolio


def test_optimize_portfolio_insufficient_tickers():
    res = optimize_portfolio(["AAPL"], {})
    assert "error" in res


def test_optimize_portfolio_valid_calculation():
    np.random.seed(42)
    ret_a = np.random.normal(0.001, 0.015, 100).tolist()
    ret_b = np.random.normal(0.0005, 0.010, 100).tolist()

    res = optimize_portfolio(["AAPL", "MSFT"], {"AAPL": ret_a, "MSFT": ret_b})

    assert "weights" in res
    assert "AAPL" in res["weights"]
    assert "MSFT" in res["weights"]
    assert abs(sum(res["weights"].values()) - 1.0) < 0.01
    assert "sharpe_ratio" in res
