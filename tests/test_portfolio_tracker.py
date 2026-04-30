"""
Unit tests for agents/portfolio_tracker.py
Pure-Python — no network, no LLM, no API keys required.
"""

import importlib.util
import os
import sys

import pytest

# Load portfolio_tracker directly to avoid agents/__init__ circular import
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

_spec = importlib.util.spec_from_file_location(
    "agents.portfolio_tracker",
    os.path.join(_REPO_ROOT, "agents", "portfolio_tracker.py"),
)
_pt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pt)

analyse_portfolio = _pt.analyse_portfolio
compute_position_pnl = _pt.compute_position_pnl
compute_sector_allocation = _pt.compute_sector_allocation
compute_diversification_score = _pt.compute_diversification_score
classify_diversification = _pt.classify_diversification
compute_portfolio_beta = _pt.compute_portfolio_beta
identify_top_performers = _pt.identify_top_performers


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

POSITIONS = [
    {"ticker": "AAPL", "quantity": 10, "avg_price": 150.0, "sector": "Technology"},
    {"ticker": "MSFT", "quantity": 5, "avg_price": 280.0, "sector": "Technology"},
    {"ticker": "JNJ", "quantity": 8, "avg_price": 160.0, "sector": "Healthcare"},
    {"ticker": "XOM", "quantity": 20, "avg_price": 90.0, "sector": "Energy"},
    {"ticker": "JPM", "quantity": 6, "avg_price": 140.0, "sector": "Financials"},
]

PRICE_LOOKUP = {
    "AAPL": {"current_price": 188.0, "beta": 1.24, "sector": "Technology"},
    "MSFT": {"current_price": 320.0, "beta": 0.90, "sector": "Technology"},
    "JNJ": {"current_price": 155.0, "beta": 0.55, "sector": "Healthcare"},
    "XOM": {"current_price": 105.0, "beta": 1.10, "sector": "Energy"},
    "JPM": {"current_price": 185.0, "beta": 1.15, "sector": "Financials"},
}


# ---------------------------------------------------------------------------
# TestComputePositionPnl
# ---------------------------------------------------------------------------


class TestComputePositionPnl:
    def test_gain_position(self):
        """Buy at 100, now at 120 — should show 20% gain."""
        result = compute_position_pnl({"quantity": 10, "avg_price": 100.0}, 120.0)
        assert result["cost_basis"] == 1000.0
        assert result["market_value"] == 1200.0
        assert result["unrealised_pnl"] == 200.0
        assert result["pnl_pct"] == 20.0

    def test_loss_position(self):
        """Buy at 200, now at 160 — should show -20% loss."""
        result = compute_position_pnl({"quantity": 5, "avg_price": 200.0}, 160.0)
        assert result["cost_basis"] == 1000.0
        assert result["market_value"] == 800.0
        assert result["unrealised_pnl"] == -200.0
        assert result["pnl_pct"] == -20.0

    def test_breakeven_position(self):
        """Buy and current price equal — should be 0% P&L."""
        result = compute_position_pnl({"quantity": 10, "avg_price": 100.0}, 100.0)
        assert result["unrealised_pnl"] == 0.0
        assert result["pnl_pct"] == 0.0

    def test_zero_avg_price_returns_zero_pct(self):
        """avg_price=0 should not raise ZeroDivisionError."""
        result = compute_position_pnl({"quantity": 5, "avg_price": 0.0}, 100.0)
        assert result["pnl_pct"] == 0.0

    def test_fractional_shares(self):
        """Fractional quantity should compute correctly."""
        result = compute_position_pnl({"quantity": 0.5, "avg_price": 200.0}, 300.0)
        assert result["cost_basis"] == 100.0
        assert result["market_value"] == 150.0
        assert result["pnl_pct"] == 50.0


# ---------------------------------------------------------------------------
# TestComputeSectorAllocation
# ---------------------------------------------------------------------------


class TestComputeSectorAllocation:
    def test_single_sector(self):
        positions = [
            {"sector": "Technology", "market_value": 1000.0},
            {"sector": "Technology", "market_value": 500.0},
        ]
        result = compute_sector_allocation(positions)
        assert result == {"Technology": 100.0}

    def test_two_equal_sectors(self):
        positions = [
            {"sector": "Technology", "market_value": 500.0},
            {"sector": "Healthcare", "market_value": 500.0},
        ]
        result = compute_sector_allocation(positions)
        assert result["Technology"] == 50.0
        assert result["Healthcare"] == 50.0

    def test_missing_sector_defaults_to_unknown(self):
        positions = [{"market_value": 800.0}, {"sector": None, "market_value": 200.0}]
        result = compute_sector_allocation(positions)
        assert "Unknown" in result

    def test_empty_positions_returns_empty(self):
        assert compute_sector_allocation([]) == {}

    def test_zero_total_returns_empty(self):
        positions = [{"sector": "Tech", "market_value": 0.0}]
        assert compute_sector_allocation(positions) == {}


# ---------------------------------------------------------------------------
# TestComputeDiversificationScore
# ---------------------------------------------------------------------------


class TestComputeDiversificationScore:
    def test_single_sector_scores_zero(self):
        score = compute_diversification_score({"Technology": 100.0})
        assert score == 0.0

    def test_two_equal_sectors_scores_100(self):
        score = compute_diversification_score({"Technology": 50.0, "Healthcare": 50.0})
        assert score == 100.0

    def test_five_equal_sectors_scores_100(self):
        alloc = {s: 20.0 for s in ["Tech", "Health", "Energy", "Finance", "Consumer"]}
        score = compute_diversification_score(alloc)
        assert score == 100.0

    def test_unequal_sectors_between_0_and_100(self):
        score = compute_diversification_score({"Technology": 80.0, "Healthcare": 20.0})
        assert 0.0 < score < 100.0

    def test_empty_returns_zero(self):
        assert compute_diversification_score({}) == 0.0


# ---------------------------------------------------------------------------
# TestClassifyDiversification
# ---------------------------------------------------------------------------


class TestClassifyDiversification:
    def test_excellent(self):
        assert classify_diversification(90.0) == "Excellent"

    def test_good(self):
        assert classify_diversification(70.0) == "Good"

    def test_fair(self):
        assert classify_diversification(50.0) == "Fair"

    def test_poor(self):
        assert classify_diversification(20.0) == "Poor"


# ---------------------------------------------------------------------------
# TestComputePortfolioBeta
# ---------------------------------------------------------------------------


class TestComputePortfolioBeta:
    def test_equal_weight_beta(self):
        positions = [
            {"market_value": 500.0, "beta": 1.0},
            {"market_value": 500.0, "beta": 2.0},
        ]
        beta = compute_portfolio_beta(positions)
        assert beta == pytest.approx(1.5, abs=0.01)

    def test_no_beta_returns_none(self):
        positions = [{"market_value": 1000.0}]
        assert compute_portfolio_beta(positions) is None

    def test_partial_beta_uses_available(self):
        """Only positions with beta contribute to the weighted average."""
        positions = [
            {"market_value": 500.0, "beta": 1.0},
            {"market_value": 500.0},  # no beta
        ]
        beta = compute_portfolio_beta(positions)
        # 500/1000 * 1.0 = 0.5
        assert beta == pytest.approx(0.5, abs=0.01)

    def test_zero_total_returns_none(self):
        positions = [{"market_value": 0.0, "beta": 1.0}]
        assert compute_portfolio_beta(positions) is None


# ---------------------------------------------------------------------------
# TestIdentifyTopPerformers
# ---------------------------------------------------------------------------


class TestIdentifyTopPerformers:
    def test_gainers_sorted_descending(self):
        positions = [
            {"ticker": "A", "pnl_pct": 5.0},
            {"ticker": "B", "pnl_pct": 20.0},
            {"ticker": "C", "pnl_pct": 10.0},
        ]
        gainers, _ = identify_top_performers(positions, n=2)
        assert gainers[0]["ticker"] == "B"
        assert gainers[1]["ticker"] == "C"

    def test_losers_sorted_ascending(self):
        positions = [
            {"ticker": "A", "pnl_pct": -5.0},
            {"ticker": "B", "pnl_pct": -15.0},
            {"ticker": "C", "pnl_pct": -2.0},
        ]
        _, losers = identify_top_performers(positions, n=2)
        assert losers[0]["ticker"] == "B"
        assert losers[1]["ticker"] == "A"

    def test_no_losers_returns_empty_losers(self):
        positions = [
            {"ticker": "A", "pnl_pct": 10.0},
            {"ticker": "B", "pnl_pct": 5.0},
        ]
        _, losers = identify_top_performers(positions)
        assert losers == []


# ---------------------------------------------------------------------------
# TestAnalysePortfolio (integration of all helpers)
# ---------------------------------------------------------------------------


class TestAnalysePortfolio:
    def test_full_analysis_returns_required_keys(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        required = {
            "total_cost_basis",
            "total_market_value",
            "total_unrealised_pnl",
            "total_pnl_pct",
            "positions",
            "sector_allocation",
            "diversification_score",
            "diversification_label",
            "portfolio_beta",
            "top_gainers",
            "top_losers",
            "health_summary",
            "generated_at",
        }
        assert required.issubset(result.keys())

    def test_total_cost_basis_correct(self):
        """Cost basis = sum(qty * avg_price) across all positions."""
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        expected = (10 * 150) + (5 * 280) + (8 * 160) + (20 * 90) + (6 * 140)
        assert result["total_cost_basis"] == pytest.approx(expected, abs=0.01)

    def test_total_market_value_positive(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        assert result["total_market_value"] > 0

    def test_positions_count_matches_input(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        assert len(result["positions"]) == len(POSITIONS)

    def test_sector_allocation_sums_to_100(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        total = sum(result["sector_allocation"].values())
        assert total == pytest.approx(100.0, abs=0.1)

    def test_diversification_score_range(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        assert 0.0 <= result["diversification_score"] <= 100.0

    def test_portfolio_beta_is_numeric(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        assert isinstance(result["portfolio_beta"], float)

    def test_gainers_are_profit_positions(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        for g in result["top_gainers"]:
            assert g["pnl_pct"] >= 0

    def test_losers_are_loss_positions(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        for lo in result["top_losers"]:
            assert lo["pnl_pct"] < 0

    def test_health_summary_is_string(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        assert isinstance(result["health_summary"], str)
        assert len(result["health_summary"]) > 0

    def test_empty_positions_returns_error(self):
        result = analyse_portfolio([], PRICE_LOOKUP)
        assert "error" in result

    def test_missing_price_data_marks_error(self):
        """Positions with no price data should have error field, not crash."""
        positions = [{"ticker": "UNKN", "quantity": 5, "avg_price": 100.0}]
        result = analyse_portfolio(positions, {})
        pos = result["positions"][0]
        assert "error" in pos

    def test_single_sector_poor_diversification(self):
        """All same sector should give Poor diversification label."""
        same_sector = [
            {"ticker": "AAPL", "quantity": 10, "avg_price": 150.0, "sector": "Technology"},
            {"ticker": "MSFT", "quantity": 5, "avg_price": 280.0, "sector": "Technology"},
        ]
        result = analyse_portfolio(same_sector, PRICE_LOOKUP)
        assert result["diversification_label"] == "Poor"

    def test_pnl_pct_calculated_per_position(self):
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        # AAPL: avg 150, current 188 → ~25.3% gain
        aapl_pos = next(p for p in result["positions"] if p["ticker"] == "AAPL")
        assert aapl_pos["pnl_pct"] == pytest.approx(25.33, abs=0.1)

    def test_jnj_shows_loss(self):
        """JNJ: avg 160, current 155 → loss position."""
        result = analyse_portfolio(POSITIONS, PRICE_LOOKUP)
        jnj_pos = next(p for p in result["positions"] if p["ticker"] == "JNJ")
        assert jnj_pos["unrealised_pnl"] < 0
        assert jnj_pos["pnl_pct"] < 0
