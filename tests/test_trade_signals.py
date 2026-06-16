"""Unit tests for tools/trade_signals.py trade signal aggregation engine."""

from tools.trade_signals import (
    aggregate_signals,
    format_trade_signals_report,
    signal_confidence_label,
    signal_strength_score,
)

# ── aggregate_signals ─────────────────────────────────────────────────────────


class TestAggregateSignals:
    def test_no_inputs_gives_neutral(self):
        result = aggregate_signals()
        assert result["direction"] == "Neutral"
        assert result["raw_score"] == 0.0
        assert result["signals_used"] == []

    def test_oversold_rsi_gives_bullish_vote(self):
        result = aggregate_signals(rsi=20.0)
        assert result["votes"].get("rsi") == "Bullish (Oversold)"
        assert result["bull_score"] > 0.0

    def test_overbought_rsi_gives_bearish_vote(self):
        result = aggregate_signals(rsi=80.0)
        assert result["votes"].get("rsi") == "Bearish (Overbought)"
        assert result["bear_score"] > 0.0

    def test_neutral_rsi_gives_neutral_vote(self):
        result = aggregate_signals(rsi=50.0)
        assert result["votes"].get("rsi") == "Neutral"

    def test_bullish_macd_crossover(self):
        macd = {"crossover": "Bullish Crossover", "macd": 0.5, "signal": 0.3}
        result = aggregate_signals(macd=macd)
        assert "Bullish" in result["votes"].get("macd", "")

    def test_bearish_macd_crossover(self):
        macd = {"crossover": "Bearish Crossover", "macd": -0.5, "signal": 0.3}
        result = aggregate_signals(macd=macd)
        assert "Bearish" in result["votes"].get("macd", "")

    def test_golden_cross_gives_bullish_ma(self):
        result = aggregate_signals(ma_signal="Golden Cross (Bullish)")
        assert "Bullish" in result["votes"].get("ma", "")

    def test_death_cross_gives_bearish_ma(self):
        result = aggregate_signals(ma_signal="Death Cross (Bearish)")
        assert "Bearish" in result["votes"].get("ma", "")

    def test_bb_oversold_gives_bullish(self):
        bb = {"upper": 110.0, "lower": 90.0, "position": "Oversold"}
        result = aggregate_signals(bb=bb, current_price=88.0)
        assert "Bullish" in result["votes"].get("bb", "")

    def test_bb_overbought_gives_bearish(self):
        bb = {"upper": 110.0, "lower": 90.0, "position": "Overbought"}
        result = aggregate_signals(bb=bb, current_price=115.0)
        assert "Bearish" in result["votes"].get("bb", "")

    def test_bullish_volume_signal(self):
        result = aggregate_signals(volume_signal="Bullish Accumulation")
        assert "Bullish" in result["votes"].get("volume", "")

    def test_bearish_volume_signal(self):
        result = aggregate_signals(volume_signal="Bearish Distribution")
        assert "Bearish" in result["votes"].get("volume", "")

    def test_stochastic_oversold_gives_bullish(self):
        stoch = {"k": 15.0, "d": 18.0, "signal": "Bullish", "zone": "Oversold"}
        result = aggregate_signals(stochastic=stoch)
        assert "Bullish" in result["votes"].get("stoch", "")

    def test_all_bullish_gives_bullish_direction(self):
        result = aggregate_signals(
            rsi=25.0,
            macd={"crossover": "Bullish Crossover", "macd": 1.0, "signal": 0.5},
            ma_signal="Golden Cross (Bullish)",
            volume_signal="Bullish Accumulation",
        )
        assert result["direction"] == "Bullish"
        assert result["raw_score"] > 0

    def test_all_bearish_gives_bearish_direction(self):
        result = aggregate_signals(
            rsi=80.0,
            macd={"crossover": "Bearish Crossover", "macd": -1.0, "signal": 0.5},
            ma_signal="Death Cross (Bearish)",
            volume_signal="Bearish Distribution",
        )
        assert result["direction"] == "Bearish"
        assert result["raw_score"] < 0

    def test_signals_used_tracking(self):
        result = aggregate_signals(rsi=50.0, volume_signal="Neutral")
        assert "rsi" in result["signals_used"]
        assert "volume" in result["signals_used"]
        assert "macd" not in result["signals_used"]


# ── signal_strength_score ─────────────────────────────────────────────────────

class TestSignalStrengthScore:
    def test_neutral_gives_low_strength(self):
        result = aggregate_signals()
        strength = signal_strength_score(result)
        assert strength == 0.0

    def test_all_bullish_gives_high_strength(self):
        result = aggregate_signals(
            rsi=20.0,
            macd={"crossover": "Bullish Crossover", "macd": 1.0, "signal": 0.5},
            ma_signal="Golden Cross (Bullish)",
            volume_signal="Bullish Accumulation",
            stochastic={"k": 10.0, "signal": "Bullish", "zone": "Oversold"},
        )
        strength = signal_strength_score(result)
        assert strength > 0.5

    def test_strength_is_between_zero_and_one(self):
        for rsi_val in [15.0, 50.0, 85.0]:
            result = aggregate_signals(rsi=rsi_val)
            strength = signal_strength_score(result)
            assert 0.0 <= strength <= 1.0

    def test_more_signals_may_increase_strength(self):
        result_one = aggregate_signals(rsi=20.0)
        result_two = aggregate_signals(rsi=20.0, ma_signal="Golden Cross (Bullish)")
        s1 = signal_strength_score(result_one)
        s2 = signal_strength_score(result_two)
        assert s2 >= s1


# ── signal_confidence_label ───────────────────────────────────────────────────

class TestSignalConfidenceLabel:
    def test_zero_gives_no_signal(self):
        assert signal_confidence_label(0.0) == "No Signal"

    def test_low_strength_gives_low_conviction(self):
        assert signal_confidence_label(0.25) == "Low Conviction"

    def test_medium_gives_moderate(self):
        assert signal_confidence_label(0.5) == "Moderate Conviction"

    def test_high_gives_high_conviction(self):
        assert signal_confidence_label(0.8) == "High Conviction"

    def test_boundary_0_75_gives_high(self):
        assert signal_confidence_label(0.75) == "High Conviction"

    def test_boundary_0_45_gives_moderate(self):
        assert signal_confidence_label(0.45) == "Moderate Conviction"


# ── format_trade_signals_report ───────────────────────────────────────────────

class TestFormatTradeSignalsReport:
    def _bullish_aggregated(self):
        return aggregate_signals(
            rsi=25.0,
            macd={"crossover": "Bullish Crossover", "macd": 1.0, "signal": 0.5},
            ma_signal="Golden Cross (Bullish)",
        )

    def test_report_contains_ticker(self):
        report = format_trade_signals_report("AAPL", self._bullish_aggregated())
        assert "AAPL" in report

    def test_report_contains_direction(self):
        report = format_trade_signals_report("AAPL", self._bullish_aggregated())
        assert "Bullish" in report

    def test_report_contains_confidence(self):
        report = format_trade_signals_report("AAPL", self._bullish_aggregated())
        assert "Conviction" in report or "Signal" in report

    def test_report_shows_vote_table(self):
        report = format_trade_signals_report("AAPL", self._bullish_aggregated())
        assert "RSI" in report
        assert "MACD" in report

    def test_neutral_aggregated_shows_neutral(self):
        neutral = aggregate_signals()
        report = format_trade_signals_report("TEST", neutral)
        assert "Neutral" in report or "No Signal" in report
