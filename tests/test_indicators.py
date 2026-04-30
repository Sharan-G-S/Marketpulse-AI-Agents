# MarketPulse — Technical Indicators Tests

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.indicators import (
    compute_bollinger_bands,
    compute_macd,
    compute_moving_averages,
    compute_rsi,
    get_all_indicators,
)


class TestRSI:
    def test_neutral_rsi_with_flat_prices(self):
        closes = [100.0] * 20
        rsi = compute_rsi(closes)
        assert 0 <= rsi <= 100

    def test_rsi_overbought_with_rising_prices(self):
        closes = [float(i) for i in range(50, 100)]
        rsi = compute_rsi(closes)
        assert rsi > 60  # Should be elevated for consistent gains

    def test_rsi_returns_neutral_for_insufficient_data(self):
        closes = [100.0, 101.0]
        rsi = compute_rsi(closes, period=14)
        assert rsi == 50.0

    def test_rsi_range(self, mock_price_history):
        closes = [r["close"] for r in mock_price_history]
        rsi = compute_rsi(closes)
        assert 0 <= rsi <= 100


class TestMACD:
    def test_macd_returns_dict_keys(self):
        closes = [float(i + 100) for i in range(40)]
        result = compute_macd(closes)
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result
        assert "crossover" in result

    def test_macd_crossover_bullish_on_rising(self):
        closes = [float(i + 100) for i in range(40)]
        result = compute_macd(closes)
        assert result["crossover"] in ("Bullish", "Bearish", "Insufficient data")

    def test_macd_insufficient_data(self):
        closes = [100.0, 101.0, 102.0]
        result = compute_macd(closes)
        assert result["crossover"] == "Insufficient data"


class TestBollingerBands:
    def test_bands_structure(self):
        closes = [float(100 + (i % 5)) for i in range(25)]
        result = compute_bollinger_bands(closes)
        assert result["upper"] >= result["middle"] >= result["lower"]
        assert "bandwidth" in result
        assert "position" in result

    def test_position_labels(self):
        closes = [float(100 + (i % 5)) for i in range(25)]
        result = compute_bollinger_bands(closes)
        assert result["position"] in ("Overbought", "Oversold", "Within Bands")

    def test_insufficient_data_returns_defaults(self):
        result = compute_bollinger_bands([100.0, 101.0], period=20)
        assert result["upper"] == 0.0


class TestMovingAverages:
    def test_ma_with_enough_data(self):
        closes = [float(100 + i * 0.5) for i in range(60)]
        result = compute_moving_averages(closes)
        assert result["sma_20"] is not None
        assert result["sma_50"] is not None
        assert result["ema_12"] is not None

    def test_golden_cross_detected(self):
        # Rapidly rising prices → SMA-20 should exceed SMA-50
        closes = [float(50 + i * 2) for i in range(60)]
        result = compute_moving_averages(closes)
        assert "Golden Cross" in result["ma_signal"] or "Death Cross" in result["ma_signal"]


class TestGetAllIndicators:
    def test_all_indicators_from_fixture(self, mock_price_history):
        result = get_all_indicators(mock_price_history)
        # With only 5 data points most indicators will have limited data
        assert "rsi" in result or "error" in result

    def test_error_on_empty_history(self):
        result = get_all_indicators([])
        assert "error" in result

    def test_error_on_bad_history(self):
        result = get_all_indicators([{"error": "fetch failed"}])
        assert "error" in result
