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
