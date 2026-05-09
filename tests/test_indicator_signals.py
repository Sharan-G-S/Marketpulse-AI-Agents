"""
Unit Tests — tools/indicator_signals.py
"""

import importlib.util
import os
import sys

import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

_spec = importlib.util.spec_from_file_location(
    "tools.indicator_signals",
    os.path.join(_REPO, "tools", "indicator_signals.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

rsi_signal      = _mod.rsi_signal
macd_signal     = _mod.macd_signal
ma_signal       = _mod.ma_signal
bollinger_signal = _mod.bollinger_signal
overall_signal  = _mod.overall_signal


# ── rsi_signal ───────────────────────────────────────────────────────────────

class TestRsiSignal:
    def test_none_returns_na(self):
        assert rsi_signal(None) == "N/A"

    def test_overbought(self):
        assert "Overbought" in rsi_signal(80.0)

    def test_oversold(self):
        assert "Oversold" in rsi_signal(20.0)

    def test_neutral(self):
        assert "Neutral" in rsi_signal(50.0)

    def test_bullish_zone(self):
        assert "Bullish" in rsi_signal(62.0)

    def test_bearish_zone(self):
        assert "Bearish" in rsi_signal(38.0)


# ── macd_signal ───────────────────────────────────────────────────────────────

class TestMacdSignal:
    def test_none_returns_na(self):
        assert macd_signal(None) == "N/A"

    def test_empty_dict_returns_na(self):
        assert macd_signal({}) == "N/A"

    def test_bullish_crossover(self):
        assert "Bullish" in macd_signal({"crossover": "Bullish Crossover"})

    def test_bearish_crossover(self):
        assert "Bearish" in macd_signal({"crossover": "Bearish Crossover"})

    def test_macd_above_signal(self):
        result = macd_signal({"crossover": "", "macd": 0.5, "signal": 0.1})
        assert "Bullish" in result

    def test_macd_below_signal(self):
        result = macd_signal({"crossover": "", "macd": -0.5, "signal": 0.1})
        assert "Bearish" in result


# ── ma_signal ─────────────────────────────────────────────────────────────────

class TestMaSignal:
    def test_none_returns_na(self):
        assert ma_signal(None) == "N/A"

    def test_golden_cross(self):
        assert "Golden" in ma_signal("Golden Cross (Bullish)")

    def test_death_cross(self):
        assert "Death" in ma_signal("Death Cross (Bearish)")

    def test_other_string_passthrough(self):
        result = ma_signal("Sideways")
        assert "Sideways" in result


# ── bollinger_signal ──────────────────────────────────────────────────────────

class TestBollingerSignal:
    def test_none_bb_returns_na(self):
        assert bollinger_signal(None, 100.0) == "N/A"

    def test_near_upper_band(self):
        bb = {"upper": 110.0, "lower": 90.0, "middle": 100.0}
        result = bollinger_signal(bb, 112.0)
        assert "Upper" in result

    def test_near_lower_band(self):
        bb = {"upper": 110.0, "lower": 90.0, "middle": 100.0}
        result = bollinger_signal(bb, 88.0)
        assert "Lower" in result

    def test_above_middle(self):
        bb = {"upper": 110.0, "lower": 90.0, "middle": 100.0}
        result = bollinger_signal(bb, 105.0)
        assert "Above" in result


# ── overall_signal ────────────────────────────────────────────────────────────

class TestOverallSignal:
    def test_all_bullish(self):
        result = overall_signal(30.0, {"crossover": "Bullish"}, "Golden Cross (Bullish)")
        assert "Bullish" in result

    def test_all_bearish(self):
        result = overall_signal(70.0, {"crossover": "Bearish"}, "Death Cross (Bearish)")
        assert "Bearish" in result

    def test_mixed_neutral(self):
        result = overall_signal(50.0, {"crossover": ""}, None)
        assert "Neutral" in result

    def test_all_none_neutral(self):
        result = overall_signal(None, None, None)
        assert "Neutral" in result
