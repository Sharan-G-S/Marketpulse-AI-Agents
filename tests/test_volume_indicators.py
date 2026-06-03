"""Unit tests for tools/volume_indicators.py volume indicators."""

import pytest

from tools.volume_indicators import compute_adl, compute_cmf, compute_obv, generate_volume_signals


def _make_history(closes, volumes, highs=None, lows=None):
    """Generate synthetic OHLCV price history for testing."""
    history = []
    for i in range(len(closes)):
        high_val = highs[i] if highs else closes[i] + 1.0
        low_val = lows[i] if lows else closes[i] - 1.0
        history.append({
            "high": high_val,
            "low": low_val,
            "close": closes[i],
            "volume": volumes[i]
        })
    return history


class TestOBV:
    def test_empty_input(self):
        assert compute_obv([]) == []

    def test_basic_calculations(self):
        # OBV should:
        # Day 1: close=10, vol=100 -> OBV = 100
        # Day 2: close=12 (up), vol=200 -> OBV = 100 + 200 = 300
        # Day 3: close=11 (down), vol=150 -> OBV = 300 - 150 = 150
        # Day 4: close=11 (flat), vol=300 -> OBV = 150
        history = _make_history([10.0, 12.0, 11.0, 11.0], [100, 200, 150, 300])
        result = compute_obv(history)
        assert result == [100.0, 300.0, 150.0, 150.0]

    def test_invalid_values(self):
        history = [
            {"close": "invalid", "volume": 100},
            {"close": 12.0, "volume": "bad"}
        ]
        result = compute_obv(history)
        assert len(result) == 2


class TestADL:
    def test_empty_input(self):
        assert compute_adl([]) == []

    def test_basic_calculations(self):
        # Money Flow Multiplier: ((Close - Low) - (High - Close)) / (High - Low)
        # Day 1: close=10, high=12, low=8, vol=100
        # MFM = ((10 - 8) - (12 - 10)) / (12 - 8) = (2 - 2) / 4 = 0.0
        # MFV = 0 * 100 = 0.0 -> ADL = 0.0
        # Day 2: close=11, high=12, low=8, vol=200
        # MFM = ((11 - 8) - (12 - 11)) / (12 - 8) = (3 - 1) / 4 = 2 / 4 = 0.5
        # MFV = 0.5 * 200 = 100.0 -> ADL = 0.0 + 100.0 = 100.0
        history = _make_history([10.0, 11.0], [100, 200], highs=[12.0, 12.0], lows=[8.0, 8.0])
        result = compute_adl(history)
        assert result == [0.0, 100.0]

    def test_flat_bar_no_division_by_zero(self):
        # If high == low, MFM should be 0.0, and no error
        history = _make_history([10.0, 10.0], [100, 100], highs=[10.0, 10.0], lows=[10.0, 10.0])
        result = compute_adl(history)
        assert result == [0.0, 0.0]


class TestCMF:
    def test_empty_input(self):
        assert compute_cmf([]) == []

    def test_invalid_period(self):
        history = _make_history([10.0, 11.0], [100, 200])
        assert compute_cmf(history, period=0) == [None, None]
        assert compute_cmf(history, period=-5) == [None, None]

    def test_insufficient_data(self):
        history = _make_history([10.0, 11.0], [100, 200])
        assert compute_cmf(history, period=3) == [None, None]

    def test_basic_calculations(self):
        # Period = 2
        # Day 1: close=10, high=12, low=8, vol=100 -> MFM = 0.0, MFV = 0.0
        # Day 2: close=11, high=12, low=8, vol=200 -> MFM = 0.5, MFV = 100.0
        # Sum of MFV (period 2) = 0.0 + 100.0 = 100.0
        # Sum of Volume (period 2) = 100 + 200 = 300
        # CMF = 100.0 / 300 = 0.3333
        history = _make_history([10.0, 11.0], [100, 200], highs=[12.0, 12.0], lows=[8.0, 8.0])
        result = compute_cmf(history, period=2)
        assert result[0] is None
        assert result[1] == pytest.approx(0.3333, abs=1e-4)

    def test_zero_volume(self):
        history = _make_history([10.0, 11.0], [0, 0])
        result = compute_cmf(history, period=2)
        assert result[1] == 0.0


class TestVolumeSignals:
    def test_insufficient_data(self):
        result = generate_volume_signals([])
        assert result["composite_signal"] == "Insufficient Data"

        result = generate_volume_signals([{"close": 100}])
        assert result["composite_signal"] == "Insufficient Data"

    def test_bullish_signal(self):
        # We need at least 2 bars. Let's make prices and volumes go up.
        # Close at high to make Money Flow Multiplier +1.0
        history = _make_history(
            [11.0, 12.0, 13.0, 14.0, 15.0, 16.0],
            [100, 150, 200, 250, 300, 400],
            highs=[11.0, 12.0, 13.0, 14.0, 15.0, 16.0],
            lows=[9.0, 10.0, 11.0, 12.0, 13.0, 14.0]
        )
        result = generate_volume_signals(history)
        assert result["composite_signal"] == "Bullish"
        assert "Strong buying pressure" in result["interpretation"]

    def test_bearish_signal(self):
        # Prices dropping, volume high on drops
        # Close at low to make Money Flow Multiplier -1.0
        history = _make_history(
            [14.0, 13.0, 12.0, 11.0, 10.0, 9.0],
            [100, 150, 200, 250, 300, 400],
            highs=[16.0, 15.0, 14.0, 13.0, 12.0, 11.0],
            lows=[14.0, 13.0, 12.0, 11.0, 10.0, 9.0]
        )
        result = generate_volume_signals(history)
        assert result["composite_signal"] == "Bearish"
        assert "Selling pressure" in result["interpretation"]
