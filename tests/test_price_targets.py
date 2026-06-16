"""Unit tests for tools/price_targets.py price target analysis."""

from tools.price_targets import (
    compute_price_target,
    compute_support_resistance,
    format_price_target_report,
)


def _make_bar(close, high=None, low=None):
    """Create a single OHLCV bar dict."""
    return {
        "close": close,
        "high": high if high is not None else close + 1.0,
        "low": low if low is not None else close - 1.0,
        "volume": 1000,
    }


def _make_history(closes, spread=1.0):
    """Create an OHLCV history list from closing prices."""
    return [_make_bar(c, c + spread, c - spread) for c in closes]


# ── compute_support_resistance ────────────────────────────────────────────────

class TestComputeSupportResistance:
    def test_empty_returns_none_values(self):
        result = compute_support_resistance([])
        for key in ("pivot", "r1", "r2", "s1", "s2"):
            assert result[key] is None

    def test_single_bar_returns_none_values(self):
        result = compute_support_resistance([_make_bar(100.0)])
        for key in ("pivot", "r1", "r2", "s1", "s2"):
            assert result[key] is None

    def test_basic_calculation(self):
        # high=110, low=90, close=100 → pivot = (110+90+100)/3 = 100.0
        history = [_make_bar(100.0, high=110.0, low=90.0)]
        # We need at least 2 bars so add a second
        history = [_make_bar(95.0, 105.0, 85.0)] + history
        result = compute_support_resistance(history)
        assert result["pivot"] is not None
        # R1 > pivot and S1 < pivot
        assert result["r1"] > result["pivot"]
        assert result["s1"] < result["pivot"]

    def test_r2_above_r1(self):
        history = _make_history([100.0, 102.0, 104.0, 103.0, 105.0])
        result = compute_support_resistance(history)
        if result["r2"] is not None and result["r1"] is not None:
            assert result["r2"] >= result["r1"]

    def test_s2_below_s1(self):
        history = _make_history([100.0, 102.0, 104.0, 103.0, 105.0])
        result = compute_support_resistance(history)
        if result["s2"] is not None and result["s1"] is not None:
            assert result["s2"] <= result["s1"]

    def test_n_periods_limits_window(self):
        # With n_periods=2 we only use last 2 bars
        long_history = _make_history([80.0, 90.0, 100.0, 110.0, 120.0])
        short_window = _make_history([110.0, 120.0])
        result_long = compute_support_resistance(long_history, n_periods=2)
        result_short = compute_support_resistance(short_window, n_periods=2)
        assert result_long["pivot"] == result_short["pivot"]


# ── compute_price_target ──────────────────────────────────────────────────────

class TestComputePriceTarget:
    def test_empty_returns_insufficient_data(self):
        result = compute_price_target([])
        assert result["bias"] == "Insufficient Data"
        assert result["bull_target"] is None

    def test_single_bar_returns_insufficient_data(self):
        result = compute_price_target([_make_bar(100.0)])
        assert result["bias"] == "Insufficient Data"

    def test_bull_target_above_current(self):
        history = _make_history([100.0 + i for i in range(10)])
        result = compute_price_target(history)
        assert result["bull_target"] is not None
        assert result["bull_target"] > result["current_price"]

    def test_bear_target_below_current(self):
        history = _make_history([100.0 + i for i in range(10)])
        result = compute_price_target(history)
        assert result["bear_target"] is not None
        assert result["bear_target"] < result["current_price"]

    def test_uptrend_gives_bullish_bias(self):
        history = _make_history([100.0 + i * 2 for i in range(10)])
        result = compute_price_target(history)
        assert result["bias"] == "Bullish"

    def test_downtrend_gives_bearish_bias(self):
        history = _make_history([100.0 - i * 2 for i in range(10)])
        result = compute_price_target(history)
        assert result["bias"] == "Bearish"

    def test_atr_is_positive(self):
        history = _make_history([100.0 + i for i in range(10)])
        result = compute_price_target(history)
        assert result["atr"] is not None
        assert result["atr"] >= 0.0

    def test_target_range_is_positive(self):
        history = _make_history([100.0 + i for i in range(10)])
        result = compute_price_target(history)
        assert result["target_range_pct"] is not None
        assert result["target_range_pct"] > 0.0

    def test_custom_multiplier_widens_range(self):
        history = _make_history([100.0 + i for i in range(15)])
        result_default = compute_price_target(history, atr_multiplier=1.5)
        result_wide = compute_price_target(history, atr_multiplier=3.0)
        # A larger multiplier means a wider target range
        if result_default["target_range_pct"] and result_wide["target_range_pct"]:
            assert result_wide["target_range_pct"] > result_default["target_range_pct"]


# ── format_price_target_report ────────────────────────────────────────────────

class TestFormatPriceTargetReport:
    def _dummy_pt(self):
        return {
            "current_price": 150.0,
            "atr": 2.5,
            "bull_target": 153.75,
            "bear_target": 146.25,
            "target_range_pct": 5.0,
            "bias": "Bullish",
        }

    def _dummy_sr(self):
        return {
            "pivot": 150.0,
            "r1": 155.0,
            "r2": 160.0,
            "s1": 145.0,
            "s2": 140.0,
        }

    def test_report_contains_ticker(self):
        report = format_price_target_report("AAPL", self._dummy_pt(), self._dummy_sr())
        assert "AAPL" in report

    def test_report_contains_bias(self):
        report = format_price_target_report("AAPL", self._dummy_pt(), self._dummy_sr())
        assert "Bullish" in report

    def test_report_contains_levels(self):
        report = format_price_target_report("AAPL", self._dummy_pt(), self._dummy_sr())
        assert "R1" in report or "Resistance" in report
        assert "S1" in report or "Support" in report
        assert "Pivot" in report

    def test_none_values_show_na(self):
        pt = {"current_price": None, "atr": None, "bull_target": None,
              "bear_target": None, "target_range_pct": None, "bias": "N/A"}
        sr = {"pivot": None, "r1": None, "r2": None, "s1": None, "s2": None}
        report = format_price_target_report("TEST", pt, sr)
        assert "N/A" in report
