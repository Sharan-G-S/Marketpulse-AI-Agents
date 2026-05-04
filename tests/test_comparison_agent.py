"""
Tests for agents/comparison_agent.py
"""

import importlib.util
import os
import sys

import pytest

# Load comparison_agent directly from file to bypass agents/__init__.py
# (which triggers a circular import via graph/workflow.py → alert_engine)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

_spec = importlib.util.spec_from_file_location(
    "agents.comparison_agent",
    os.path.join(_REPO_ROOT, "agents", "comparison_agent.py"),
)
_comparison_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_comparison_mod)

# Bind names from the directly-loaded module
_score_52w_range    = _comparison_mod._score_52w_range
_score_momentum     = _comparison_mod._score_momentum
_score_stability    = _comparison_mod._score_stability
_score_technical    = _comparison_mod._score_technical
_score_valuation    = _comparison_mod._score_valuation
compare_tickers     = _comparison_mod.compare_tickers
compute_composite_score = _comparison_mod.compute_composite_score
score_label         = _comparison_mod.score_label


# ---------------------------------------------------------------------------
# Individual scoring functions
# ---------------------------------------------------------------------------

class TestScoreMomentum:
    def test_zero_change_is_midpoint(self):
        assert _score_momentum(0.0) == 50.0

    def test_positive_10_is_100(self):
        assert _score_momentum(10.0) == 100.0

    def test_negative_10_is_0(self):
        assert _score_momentum(-10.0) == 0.0

    def test_clipped_above_10(self):
        assert _score_momentum(20.0) == _score_momentum(10.0)

    def test_clipped_below_minus_10(self):
        assert _score_momentum(-20.0) == _score_momentum(-10.0)

    def test_positive_5_is_75(self):
        assert _score_momentum(5.0) == 75.0


class TestScoreValuation:
    def test_low_pe_is_high_score(self):
        assert _score_valuation(10.0) == 100.0

    def test_high_pe_is_low_score(self):
        assert _score_valuation(60.0) == 0.0

    def test_none_pe_is_neutral(self):
        assert _score_valuation(None) == 50.0

    def test_zero_pe_is_neutral(self):
        assert _score_valuation(0.0) == 50.0

    def test_intermediate_pe(self):
        score = _score_valuation(35.0)
        assert 40.0 < score < 60.0


class TestScoreTechnical:
    def test_all_none_returns_50(self):
        assert _score_technical(None, None, None) == 50.0

    def test_neutral_rsi_bullish_macd_golden_ma(self):
        score = _score_technical(
            50.0,
            {"crossover": "Bullish"},
            "Golden Cross (Bullish)",
        )
        assert score >= 70.0

    def test_extreme_rsi_penalised(self):
        score_extreme = _score_technical(90.0, None, None)
        score_neutral = _score_technical(50.0, None, None)
        assert score_extreme < score_neutral

    def test_bearish_macd_lowers_score(self):
        s_bull = _score_technical(50.0, {"crossover": "Bullish"}, None)
        s_bear = _score_technical(50.0, {"crossover": "Bearish"}, None)
        assert s_bull > s_bear


class TestScoreStability:
    def test_low_beta_is_stable(self):
        assert _score_stability(0.3) == 100.0

    def test_high_beta_is_unstable(self):
        assert _score_stability(2.5) == 0.0

    def test_none_beta_is_neutral(self):
        assert _score_stability(None) == 50.0

    def test_beta_1_is_moderate(self):
        score = _score_stability(1.0)
        assert 50.0 < score < 90.0


class TestScore52wRange:
    def test_at_52w_high(self):
        assert _score_52w_range(200.0, 200.0, 100.0) == 100.0

    def test_at_52w_low(self):
        assert _score_52w_range(100.0, 200.0, 100.0) == 0.0

    def test_midpoint(self):
        assert _score_52w_range(150.0, 200.0, 100.0) == 50.0

    def test_equal_high_low_returns_50(self):
        assert _score_52w_range(100.0, 100.0, 100.0) == 50.0

    def test_none_high_returns_50(self):
        assert _score_52w_range(150.0, None, 100.0) == 50.0


# ---------------------------------------------------------------------------
# score_label
# ---------------------------------------------------------------------------

class TestScoreLabel:
    def test_strong_buy(self):
        assert score_label(80.0) == "Strong Buy"

    def test_buy(self):
        assert score_label(65.0) == "Buy"

    def test_hold(self):
        assert score_label(50.0) == "Hold"

    def test_sell(self):
        assert score_label(35.0) == "Sell"

    def test_strong_sell(self):
        assert score_label(15.0) == "Strong Sell"


# ---------------------------------------------------------------------------
# compute_composite_score
# ---------------------------------------------------------------------------

SAMPLE_TICKER = {
    "ticker": "AAPL",
    "change_pct": 2.0,
    "pe_ratio": 28.0,
    "rsi": 55.0,
    "macd": {"crossover": "Bullish"},
    "ma_signal": "Golden Cross (Bullish)",
    "beta": 1.2,
    "current_price": 175.0,
    "52w_high": 200.0,
    "52w_low": 130.0,
}


class TestComputeCompositeScore:
    def test_returns_float(self):
        score = compute_composite_score(SAMPLE_TICKER)
        assert isinstance(score, float)

    def test_within_range(self):
        score = compute_composite_score(SAMPLE_TICKER)
        assert 0.0 <= score <= 100.0

    def test_strong_positive_ticker(self):
        strong = {**SAMPLE_TICKER, "change_pct": 8.0, "pe_ratio": 12.0,
                  "rsi": 55.0, "beta": 0.6}
        score = compute_composite_score(strong)
        assert score >= 65.0

    def test_weak_ticker_lower_score(self):
        weak = {**SAMPLE_TICKER, "change_pct": -8.0, "pe_ratio": 55.0,
                "rsi": 80.0, "ma_signal": "Death Cross (Bearish)", "beta": 2.0}
        strong = {**SAMPLE_TICKER, "change_pct": 8.0, "pe_ratio": 12.0}
        assert compute_composite_score(weak) < compute_composite_score(strong)


# ---------------------------------------------------------------------------
# compare_tickers
# ---------------------------------------------------------------------------

TICKER_A = {**SAMPLE_TICKER, "ticker": "AAPL"}
TICKER_B = {
    "ticker": "TSLA",
    "change_pct": -3.0,
    "pe_ratio": 55.0,
    "rsi": 70.0,
    "macd": {"crossover": "Bearish"},
    "ma_signal": "Death Cross (Bearish)",
    "beta": 2.0,
    "current_price": 200.0,
    "52w_high": 300.0,
    "52w_low": 150.0,
}


class TestCompareTickers:
    def test_returns_dict(self):
        result = compare_tickers([TICKER_A, TICKER_B])
        assert isinstance(result, dict)

    def test_tickers_in_result(self):
        result = compare_tickers([TICKER_A, TICKER_B])
        assert "AAPL" in result["tickers"]
        assert "TSLA" in result["tickers"]

    def test_winner_is_aapl(self):
        result = compare_tickers([TICKER_A, TICKER_B])
        assert result["winner"] == "AAPL"

    def test_rankings_length(self):
        result = compare_tickers([TICKER_A, TICKER_B])
        assert len(result["rankings"]) == 2

    def test_rankings_sorted_descending(self):
        result = compare_tickers([TICKER_A, TICKER_B])
        scores = [r["score"] for r in result["rankings"]]
        assert scores == sorted(scores, reverse=True)

    def test_breakdown_contains_all_tickers(self):
        result = compare_tickers([TICKER_A, TICKER_B])
        assert "AAPL" in result["breakdown"]
        assert "TSLA" in result["breakdown"]

    def test_empty_input_returns_error(self):
        result = compare_tickers([])
        assert "error" in result

    def test_generated_at_present(self):
        result = compare_tickers([TICKER_A, TICKER_B])
        assert "generated_at" in result

    def test_three_tickers(self):
        ticker_c = {**TICKER_A, "ticker": "MSFT"}
        result = compare_tickers([TICKER_A, TICKER_B, ticker_c])
        assert len(result["rankings"]) == 3
