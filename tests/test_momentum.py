"""Unit tests for tools/momentum.py momentum indicators."""

import pytest

from tools.momentum import compute_cci, compute_roc, compute_williams_r, get_momentum_summary


def _make_history(n: int = 20, base: float = 100.0):
    """Generate synthetic OHLCV price history for testing."""
    return [
        {
            "high": base + i + 1,
            "low": base + i - 1,
            "close": base + i,
            "volume": 1_000_000,
        }
        for i in range(n)
    ]


class TestWilliamsR:
    def test_returns_dict_with_expected_keys(self):
        history = _make_history(20)
        result = compute_williams_r(history)
        assert "value" in result
        assert "signal" in result
        assert "zone" in result

    def test_insufficient_data_returns_none(self):
        result = compute_williams_r([{"close": 100}], period=14)
        assert result["value"] is None
        assert result["signal"] == "Insufficient data"

    def test_value_range(self):
        history = _make_history(20)
        result = compute_williams_r(history)
        if result["value"] is not None:
            assert -100 <= result["value"] <= 0


class TestCCI:
    def test_returns_dict_with_expected_keys(self):
        history = _make_history(25)
        result = compute_cci(history)
        assert "value" in result
        assert "signal" in result
        assert "zone" in result

    def test_insufficient_data_returns_none(self):
        result = compute_cci([{"close": 100}], period=20)
        assert result["value"] is None

    def test_zone_classification(self):
        history = _make_history(25)
        result = compute_cci(history)
        assert result["zone"] in ("Overbought", "Oversold", "Neutral")


class TestROC:
    def test_returns_dict_with_expected_keys(self):
        closes = [float(100 + i) for i in range(15)]
        result = compute_roc(closes)
        assert "value" in result
        assert "signal" in result
        assert "pct_change" in result

    def test_insufficient_data(self):
        result = compute_roc([100.0], period=10)
        assert result["value"] is None

    def test_positive_roc_is_bullish(self):
        closes = [100.0] * 10 + [110.0]
        result = compute_roc(closes)
        assert result["signal"] == "Bullish"
        assert result["value"] > 0


class TestMomentumSummary:
    def test_summary_contains_all_keys(self):
        history = _make_history(25)
        result = get_momentum_summary(history)
        assert "williams_r" in result
        assert "cci" in result
        assert "roc" in result
