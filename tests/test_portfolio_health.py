"""Unit tests for tools/portfolio_health.py — Portfolio Health Score Engine."""

from tools.portfolio_health import (
    compute_diversification_health,
    compute_overall_portfolio_health,
    compute_portfolio_concentration_risk,
    compute_position_health_score,
    format_health_report,
    health_grade,
)

# ── compute_position_health_score ─────────────────────────────────────────────


class TestComputePositionHealthScore:
    def test_zero_cost_returns_error(self):
        result = compute_position_health_score(0.0, 100.0)
        assert result["status"] == "Error"
        assert result["total_score"] == 0.0
        assert result["return_pct"] is None

    def test_zero_price_returns_error(self):
        result = compute_position_health_score(100.0, 0.0)
        assert result["status"] == "Error"

    def test_excellent_return_gives_high_score(self):
        # +25% return, no weight penalty
        result = compute_position_health_score(100.0, 125.0, weight_pct=0.10)
        assert result["return_score"] == 70.0
        assert result["total_score"] >= 80.0
        assert result["status"] == "Excellent"

    def test_poor_return_gives_low_score(self):
        # -30% return
        result = compute_position_health_score(100.0, 70.0, weight_pct=0.10)
        assert result["return_score"] == 0.0
        assert result["status"] in ("Critical", "Poor")

    def test_breakeven_gives_neutral_zone(self):
        result = compute_position_health_score(100.0, 100.0, weight_pct=0.10)
        assert 15.0 <= result["return_score"] <= 35.0

    def test_good_return_interpolation(self):
        # +12.5% is midway between +5% and +20%
        result = compute_position_health_score(100.0, 112.5, weight_pct=0.10)
        assert 35.0 <= result["return_score"] <= 70.0

    def test_weight_within_limit_gives_full_weight_score(self):
        result = compute_position_health_score(100.0, 110.0, weight_pct=0.20)
        assert result["weight_score"] == 30.0

    def test_overweight_position_penalised(self):
        # 60% weight vs 25% max → heavy penalty
        result = compute_position_health_score(100.0, 110.0, weight_pct=0.60)
        assert result["weight_score"] < 30.0

    def test_return_pct_is_correctly_computed(self):
        result = compute_position_health_score(200.0, 250.0)
        assert result["return_pct"] == 25.0

    def test_negative_return_pct(self):
        result = compute_position_health_score(200.0, 160.0)
        assert result["return_pct"] == -20.0

    def test_total_score_clamped_to_100(self):
        result = compute_position_health_score(50.0, 500.0)  # +900%
        assert result["total_score"] <= 100.0

    def test_total_score_clamped_to_0(self):
        result = compute_position_health_score(500.0, 1.0)   # -99.8%
        assert result["total_score"] >= 0.0

    def test_custom_max_single_weight(self):
        # With a tighter 10% cap, 20% weight should be penalised
        result_tight = compute_position_health_score(
            100.0, 110.0, weight_pct=0.20, max_single_weight=0.10
        )
        result_default = compute_position_health_score(
            100.0, 110.0, weight_pct=0.20
        )
        assert result_tight["weight_score"] < result_default["weight_score"]


# ── compute_portfolio_concentration_risk ──────────────────────────────────────


class TestComputePortfolioConcentrationRisk:
    def test_empty_weights_returns_error(self):
        result = compute_portfolio_concentration_risk([])
        assert result["risk_level"] == "Error"
        assert result["hhi"] is None
        assert result["n_positions"] == 0

    def test_single_position_is_very_high_risk(self):
        result = compute_portfolio_concentration_risk([1.0])
        assert result["risk_level"] == "Very High"
        assert result["hhi"] == 1.0

    def test_equal_weights_10_positions_is_low_risk(self):
        weights = [0.10] * 10
        result = compute_portfolio_concentration_risk(weights)
        # HHI = 10 * (0.10)^2 = 0.10 < 0.15 → Low risk
        assert result["risk_level"] == "Low"
        assert result["concentration_score"] == 100.0

    def test_two_equal_positions_is_high_risk(self):
        result = compute_portfolio_concentration_risk([0.50, 0.50])
        # HHI = 0.5
        assert result["risk_level"] in ("High", "Very High")
        assert result["concentration_score"] < 60.0

    def test_n_positions_correctly_counted(self):
        result = compute_portfolio_concentration_risk([0.25, 0.25, 0.25, 0.25])
        assert result["n_positions"] == 4

    def test_zero_weights_are_ignored(self):
        result = compute_portfolio_concentration_risk([0.50, 0.50, 0.0, 0.0])
        assert result["n_positions"] == 2

    def test_unnormalised_weights_are_normalised(self):
        # Raw [200, 200, 200, 200, 200] should normalise to 5 × 0.20
        result = compute_portfolio_concentration_risk([200.0] * 5)
        # HHI = 5 * (0.20)^2 = 0.20 → Moderate
        assert result["risk_level"] == "Moderate"

    def test_concentration_score_is_between_0_and_100(self):
        for n in [1, 2, 5, 10, 20]:
            r = compute_portfolio_concentration_risk([1.0 / n] * n)
            assert 0.0 <= r["concentration_score"] <= 100.0


# ── compute_diversification_health ────────────────────────────────────────────


class TestComputeDiversificationHealth:
    def test_empty_dict_returns_no_data(self):
        result = compute_diversification_health({})
        assert result["assessment"] == "No sector data"
        assert result["diversification_score"] == 0.0

    def test_single_sector_is_poorly_diversified(self):
        result = compute_diversification_health({"Tech": 1.0})
        # 1 sector < 3 (-20), < 5 (-10), breach (-15) = 55 clamped to 55 = C
        assert result["n_sectors"] == 1
        assert result["diversification_score"] < 70.0

    def test_five_equal_sectors_with_no_breach_is_well_diversified(self):
        weights = {f"Sector{i}": 0.20 for i in range(5)}
        result = compute_diversification_health(weights, target_max_sector=0.30)
        # 5 sectors, none breach 30% → score = 100
        assert result["diversification_score"] == 100.0
        assert result["assessment"] == "Well Diversified"

    def test_breached_sectors_listed(self):
        result = compute_diversification_health(
            {"Tech": 0.60, "Finance": 0.20, "Energy": 0.20},
            target_max_sector=0.30,
        )
        assert "Tech" in result["breached_sectors"]

    def test_n_sectors_counted_correctly(self):
        result = compute_diversification_health(
            {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25}
        )
        assert result["n_sectors"] == 4

    def test_zero_weight_sectors_excluded(self):
        result = compute_diversification_health({"A": 0.50, "B": 0.50, "C": 0.0})
        assert result["n_sectors"] == 2

    def test_score_clamped_to_0_on_extreme_breach(self):
        # All weight in one sector, < 3 sectors
        result = compute_diversification_health({"Tech": 1.0})
        assert result["diversification_score"] >= 0.0
