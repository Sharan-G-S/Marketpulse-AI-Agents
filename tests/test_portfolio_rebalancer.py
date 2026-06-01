"""
Unit Tests for tools/portfolio_rebalancer.py
"""

import importlib.util
import os
import sys
import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_REPO, relpath))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_rebalancer = _load("portfolio_rebalancer", "tools/portfolio_rebalancer.py")
compute_portfolio_rebalancing = _rebalancer.compute_portfolio_rebalancing
format_rebalance_report = _rebalancer.format_rebalance_report


class TestPortfolioRebalancer:
    def test_basic_rebalancing(self):
        holdings = [
            {"ticker": "AAPL", "qty": 10, "price": 150.0, "market_value": 1500.0},
            {"ticker": "MSFT", "qty": 5, "price": 300.0, "market_value": 1500.0},
        ]
        targets = {
            "AAPL": 0.60,
            "MSFT": 0.40,
        }

        result = compute_portfolio_rebalancing(holdings, targets)

        assert result["total_value"] == pytest.approx(3000.0)

        # We need to find AAPL and MSFT from result["positions"]
        positions_by_ticker = {p["ticker"]: p for p in result["positions"]}

        assert positions_by_ticker["AAPL"]["current_weight"] == pytest.approx(0.50)
        assert positions_by_ticker["AAPL"]["target_weight"] == pytest.approx(0.60)
        assert positions_by_ticker["AAPL"]["deviation_pct"] == pytest.approx(-0.10)
        assert positions_by_ticker["AAPL"]["target_value"] == pytest.approx(1800.0)

        assert positions_by_ticker["MSFT"]["current_weight"] == pytest.approx(0.50)
        assert positions_by_ticker["MSFT"]["target_weight"] == pytest.approx(0.40)
        assert positions_by_ticker["MSFT"]["deviation_pct"] == pytest.approx(0.10)
        assert positions_by_ticker["MSFT"]["target_value"] == pytest.approx(1200.0)

        # Apple needs $300 buy
        # We need to find recommendations from result["rebalance_actions"]
        actions_by_ticker = {a["ticker"]: a for a in result["rebalance_actions"]}

        assert actions_by_ticker["AAPL"]["action"] == "BUY"
        assert actions_by_ticker["AAPL"]["amount"] == pytest.approx(300.0)
        assert actions_by_ticker["AAPL"]["shares"] == pytest.approx(2.0)

        # Microsoft needs $300 sell
        assert actions_by_ticker["MSFT"]["action"] == "SELL"
        assert actions_by_ticker["MSFT"]["amount"] == pytest.approx(300.0)
        assert actions_by_ticker["MSFT"]["shares"] == pytest.approx(1.0)

        # MAD is sum(abs(p["deviation_pct"])) / len(positions) = (0.10 + 0.10) / 2 = 0.10
        # target_deviation_mad_pct = mad * 100 = 10.0
        assert result["target_deviation_mad_pct"] == pytest.approx(10.0)

    def test_target_normalization(self):
        holdings = [
            {"ticker": "AAPL", "qty": 10, "price": 100.0, "market_value": 1000.0},
            {"ticker": "MSFT", "qty": 10, "price": 100.0, "market_value": 1000.0},
        ]
        targets = {
            "AAPL": 1.0,
            "MSFT": 1.0,
        }
        result = compute_portfolio_rebalancing(holdings, targets)
        positions_by_ticker = {p["ticker"]: p for p in result["positions"]}
        assert positions_by_ticker["AAPL"]["target_weight"] == pytest.approx(0.50)
        assert positions_by_ticker["MSFT"]["target_weight"] == pytest.approx(0.50)
        assert result["target_deviation_mad_pct"] == pytest.approx(0.0)

    def test_empty_holdings(self):
        result = compute_portfolio_rebalancing([], {"AAPL": 1.0})
        assert result["total_value"] == 0.0
        assert result["target_deviation_mad_pct"] == 100.0
        assert result["rebalance_actions"] == []

    def test_missing_price_or_qty(self):
        holdings = [
            {"ticker": "AAPL"},  # Missing market_value
            {"ticker": "MSFT", "qty": 10, "price": 100.0, "market_value": 1000.0},
        ]
        targets = {"AAPL": 0.5, "MSFT": 0.5}
        result = compute_portfolio_rebalancing(holdings, targets)
        assert result["total_value"] == pytest.approx(1000.0)

        positions_by_ticker = {p["ticker"]: p for p in result["positions"]}
        assert positions_by_ticker["AAPL"]["current_value"] == 0.0

    def test_zero_or_negative_price(self):
        holdings = [
            {"ticker": "AAPL", "qty": 10, "price": 0.0, "market_value": 0.0},
            {"ticker": "MSFT", "qty": 10, "price": -50.0, "market_value": 0.0},
        ]
        targets = {"AAPL": 0.5, "MSFT": 0.5}
        result = compute_portfolio_rebalancing(holdings, targets)
        assert result["total_value"] == 0.0

    def test_dashboard_formatting(self):
        holdings = [
            {"ticker": "AAPL", "qty": 10, "price": 150.0, "market_value": 1500.0},
            {"ticker": "MSFT", "qty": 5, "price": 300.0, "market_value": 1500.0},
        ]
        targets = {
            "AAPL": 0.60,
            "MSFT": 0.40,
        }
        result = compute_portfolio_rebalancing(holdings, targets)
        report = format_rebalance_report(result)

        assert "Portfolio Rebalancing Analysis" in report
        assert "AAPL" in report
        assert "MSFT" in report
        assert "BUY" in report
        assert "SELL" in report
        assert "Mean Absolute Deviation (MAD)" in report

    def test_dashboard_formatting_empty(self):
        result = compute_portfolio_rebalancing([], {})
        report = format_rebalance_report(result)
        assert "Skipped" in report
