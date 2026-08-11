"""
MarketPulse — Technical Signal Aggregator & Consensus Engine
Aggregates RSI, MACD, Bollinger Bands, and Moving Averages into a consensus score (0-100).
"""

from typing import Any, Dict


def aggregate_technical_signals(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes a composite technical consensus score (0-100) and recommendation rating.

    Args:
        indicators: Dictionary of computed technical indicators (rsi, macd, sma_20, sma_50, etc.)

    Returns:
        Dict with score (0-100), signal_class ("Strong Buy", "Buy", "Neutral", "Sell", "Strong Sell"),
        and individual indicator signal breakdown.
    """
    if not isinstance(indicators, dict):
        return {"consensus_score": 50.0, "rating": "Neutral", "breakdown": {}}

    scores = []
    breakdown = {}

    # RSI Signal (0-100)
    rsi = indicators.get("rsi")
    if rsi is not None:
        if rsi < 30:
            s = 85.0  # Oversold = bullish buy
        elif rsi > 70:
            s = 15.0  # Overbought = bearish sell
        else:
            s = 50.0 + (50.0 - abs(rsi - 50.0)) * 0.3
        scores.append(s)
        breakdown["rsi_signal"] = round(s, 1)

    # MACD Signal
    macd = indicators.get("macd")
    if isinstance(macd, dict):
        crossover = macd.get("crossover", "")
        if crossover == "Bullish":
            s = 80.0
        elif crossover == "Bearish":
            s = 20.0
        else:
            s = 50.0
        scores.append(s)
        breakdown["macd_signal"] = s

    # Moving Average Signal
    sma20 = indicators.get("sma_20")
    sma50 = indicators.get("sma_50")
    if sma20 is not None and sma50 is not None:
        s = 75.0 if sma20 > sma50 else 25.0
        scores.append(s)
        breakdown["ma_signal"] = s

    consensus = round(float(sum(scores) / len(scores)) if scores else 50.0, 1)

    if consensus >= 75:
        rating = "Strong Buy"
    elif consensus >= 60:
        rating = "Buy"
    elif consensus >= 45:
        rating = "Neutral"
    elif consensus >= 30:
        rating = "Sell"
    else:
        rating = "Strong Sell"

    return {
        "consensus_score": consensus,
        "rating": rating,
        "breakdown": breakdown,
    }
