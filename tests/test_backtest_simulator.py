"""Unit tests for tools/backtest_simulator.py backtester."""

import math

import pytest

from tools.backtest_simulator import format_backtest_report, run_crossover_backtest


def _make_flat_history(n: int = 250, price: float = 100.0) -> list:
    """Generate simple static price history."""
    return [
        {
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": 100000,
            "date": f"2026-01-{i:02d}" if i <= 31 else f"2026-02-{i-31:02d}",
        }
        for i in range(1, n + 1)
    ]


def _make_wave_history(n: int = 250, base: float = 100.0) -> list:
    """Generate dynamic historical price data with alternating crossover signals."""
    history = []
    for i in range(n):
        close = base + 10 * math.sin(i * (2 * math.pi / 60))
        history.append({
            "open": close,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": 1000000,
            "date": f"2026-01-{i+1}"
        })
    return history


class TestBacktestSimulator:
    def test_insufficient_data(self):
        history = _make_flat_history(n=50, price=100.0)
        res = run_crossover_backtest(history, fast_period=50, slow_period=200)
        assert res["status"] == "Insufficient Data"
        assert res["trades_count"] == 0
        assert res["final_value"] == 10000.0

    def test_flat_no_trades(self):
        history = _make_flat_history(n=250, price=100.0)
        res = run_crossover_backtest(history, fast_period=10, slow_period=50)
        assert res["status"] == "Success"
        assert res["trades_count"] == 0
        assert res["final_value"] == 10000.0
        assert res["total_return_pct"] == 0.0
        assert res["benchmark_return_pct"] == 0.0
        assert res["max_drawdown_pct"] == 0.0

    def test_wave_crossover_trades(self):
        history = _make_wave_history(n=250, base=100.0)
        res = run_crossover_backtest(history, fast_period=10, slow_period=30, initial_capital=10000.0)
        assert res["status"] == "Success"
        assert res["trades_count"] > 0
        assert "final_value" in res
        assert "total_return_pct" in res
        assert "sharpe_ratio" in res
        assert "max_drawdown_pct" in res

    def test_format_insufficient_data_report(self):
        history = _make_flat_history(n=50, price=100.0)
        res = run_crossover_backtest(history, fast_period=50, slow_period=200)
        report = format_backtest_report(res)
        assert "Backtest Failed" in report

    def test_format_success_report(self):
        history = _make_wave_history(n=250, base=100.0)
        res = run_crossover_backtest(history, fast_period=10, slow_period=30)
        report = format_backtest_report(res)
        assert "Crossover Backtest Simulation Report" in report
        assert "Performance & Efficiency Metrics" in report
        assert "Transaction Ledger" in report
