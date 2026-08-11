"""
Unit tests for tools/signal_aggregator.py
"""

from tools.signal_aggregator import aggregate_technical_signals


def test_aggregate_technical_signals_bullish():
    inds = {
        "rsi": 25.0,  # Oversold -> Bullish
        "macd": {"crossover": "Bullish"},
        "sma_20": 150.0,
        "sma_50": 140.0,  # Golden alignment
    }
    res = aggregate_technical_signals(inds)
    assert res["consensus_score"] >= 70.0
    assert res["rating"] in ["Buy", "Strong Buy"]


def test_aggregate_technical_signals_empty():
    res = aggregate_technical_signals({})
    assert res["consensus_score"] == 50.0
    assert res["rating"] == "Neutral"
