"""
MarketPulse — Market Volatility & Fear & Greed Index Gauge
Evaluates market sentiment regime based on VIX proxy, RSI momentum, and market breadth.
"""

from typing import Any, Dict


def evaluate_market_fear_greed(vix_value: float = 18.5, avg_rsi: float = 55.0) -> Dict[str, Any]:
    """
    Computes Fear & Greed index score (0-100) and regime classification.
    """
    # Inverse VIX score (low VIX = high greed, high VIX = high fear)
    vix_score = max(0.0, min(100.0, 100.0 - (vix_value - 10.0) * 2.5))
    rsi_score = max(0.0, min(100.0, avg_rsi))

    composite_score = round(vix_score * 0.5 + rsi_score * 0.5, 1)

    if composite_score >= 75.0:
        regime = "Extreme Greed"
    elif composite_score >= 55.0:
        regime = "Greed"
    elif composite_score >= 45.0:
        regime = "Neutral"
    elif composite_score >= 25.0:
        regime = "Fear"
    else:
        regime = "Extreme Fear"

    return {
        "score": composite_score,
        "regime": regime,
        "vix_component": round(vix_score, 1),
        "rsi_component": round(rsi_score, 1),
    }
