"""Unit tests for tools/portfolio_summary.py portfolio aggregator."""

import pytest

from tools.portfolio_summary import (
    best_sharpe_ticker,
    compute_portfolio_summary,
    format_portfolio_summary,
    portfolio_risk_label,
    weighted_portfolio_return,
    weighted_portfolio_volatility,
    worst_drawdown_ticker,
)


@pytest.fixture
def sample_holdings():
    return [
        {
            "ticker": "AAPL",
            "weight": 0.4,
            "ann_return": 0.15,
            "ann_volatility": 0.20,
            "max_drawdown": -0.15,
            "sharpe_ratio": 1.25,
            "risk_label": "Moderate",
        },
        {
            "ticker": "TSLA",
            "weight": 0.3,
            "ann_return": 0.25,
            "ann_volatility": 0.40,
            "max_drawdown": -0.35,
            "sharpe_ratio": 0.85,
            "risk_label": "High",
        },
        {
            "ticker": "MSFT",
            "weight": 0.3,
            "ann_return": 0.10,
            "ann_volatility": 0.15,
            "max_drawdown": -0.10,
            "sharpe_ratio": 1.50,
            "risk_label": "Low",
        },
    ]


class TestPortfolioReturn:
    def test_weighted_portfolio_return_valid(self, sample_holdings):
        ret = weighted_portfolio_return(sample_holdings)
        # 0.4 * 0.15 + 0.3 * 0.25 + 0.3 * 0.10 = 0.06 + 0.075 + 0.03 = 0.165
        assert abs(ret - 0.165) < 1e-6

    def test_weighted_portfolio_return_empty(self):
        assert weighted_portfolio_return([]) == 0.0

    def test_weighted_portfolio_return_zero_weights(self):
        holdings = [{"weight": 0.0, "ann_return": 0.10}]
        assert weighted_portfolio_return(holdings) == 0.0


class TestPortfolioVolatility:
    def test_weighted_portfolio_volatility_valid(self, sample_holdings):
        vol = weighted_portfolio_volatility(sample_holdings)
        # 0.4 * 0.20 + 0.3 * 0.40 + 0.3 * 0.15 = 0.08 + 0.12 + 0.045 = 0.245
        assert abs(vol - 0.245) < 1e-6

    def test_weighted_portfolio_volatility_empty(self):
        assert weighted_portfolio_volatility([]) == 0.0

    def test_weighted_portfolio_volatility_zero_weights(self):
        holdings = [{"weight": 0.0, "ann_volatility": 0.15}]
        assert weighted_portfolio_volatility(holdings) == 0.0


class TestWorstDrawdownTicker:
    def test_worst_drawdown_ticker_valid(self, sample_holdings):
        worst = worst_drawdown_ticker(sample_holdings)
        assert worst["ticker"] == "TSLA"
        assert worst["max_drawdown"] == -0.35

    def test_worst_drawdown_ticker_empty(self):
        assert worst_drawdown_ticker([]) == {}


class TestBestSharpeTicker:
    def test_best_sharpe_ticker_valid(self, sample_holdings):
        best = best_sharpe_ticker(sample_holdings)
        assert best["ticker"] == "MSFT"
        assert best["sharpe_ratio"] == 1.50

    def test_best_sharpe_ticker_empty(self):
        assert best_sharpe_ticker([]) == {}


class TestPortfolioRiskLabel:
    def test_portfolio_risk_label_weighted(self, sample_holdings):
        # Weighted risk score:
        # Low=1, Moderate=2, High=3, Very High=4
        # AAPL (0.4 * 2) + TSLA (0.3 * 3) + MSFT (0.3 * 1) = 0.8 + 0.9 + 0.3 = 2.0
        # 2.0 is in [1.5, 2.5), so it should return "Moderate"
        assert portfolio_risk_label(sample_holdings) == "Moderate"

    def test_portfolio_risk_label_unweighted(self):
        holdings = [
            {"weight": 0.0, "risk_label": "High"},
            {"weight": 0.0, "risk_label": "Very High"},
        ]
        # (3 + 4) / 2 = 3.5 -> "Very High"
        assert portfolio_risk_label(holdings) == "Very High"

    def test_portfolio_risk_label_empty(self):
        assert portfolio_risk_label([]) == "Low"


class TestComputePortfolioSummary:
    def test_compute_portfolio_summary_valid(self, sample_holdings):
        summary = compute_portfolio_summary(sample_holdings)
        assert summary["total_holdings"] == 3
        assert abs(summary["weighted_return"] - 0.165) < 1e-6
        assert abs(summary["weighted_volatility"] - 0.245) < 1e-6
        assert summary["worst_drawdown"]["ticker"] == "TSLA"
        assert summary["best_sharpe"]["ticker"] == "MSFT"
        assert summary["portfolio_risk"] == "Moderate"

    def test_compute_portfolio_summary_empty(self):
        summary = compute_portfolio_summary([])
        assert summary["total_holdings"] == 0
        assert summary["weighted_return"] == 0.0
        assert summary["weighted_volatility"] == 0.0
        assert summary["worst_drawdown"] == {}
        assert summary["best_sharpe"] == {}
        assert summary["portfolio_risk"] == "Low"


class TestFormatPortfolioSummary:
    def test_format_portfolio_summary_valid(self, sample_holdings):
        summary = compute_portfolio_summary(sample_holdings)
        markdown = format_portfolio_summary(summary)
        assert "### 💼 Portfolio Analysis Summary" in markdown
        assert "Moderate Risk" in markdown
        assert "AAPL" not in markdown  # Best was MSFT, worst was TSLA
        assert "MSFT" in markdown
        assert "TSLA" in markdown

    def test_format_portfolio_summary_empty(self):
        markdown = format_portfolio_summary(compute_portfolio_summary([]))
        assert "No active holdings in the portfolio to analyse" in markdown
