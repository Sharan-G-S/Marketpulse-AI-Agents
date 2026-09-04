"""
MarketPulse — Crypto Asset Volatility & On-Chain Network Velocity Tool
Computes crypto asset volatility metrics and risk regime.
"""

from typing import Any, Dict


def analyze_crypto_risk_metrics(
    asset_name: str,
    price: float,
    daily_volatility_pct: float = 0.05,
    hash_rate_growth_pct: float = 0.10,
) -> Dict[str, Any]:
    """
    Evaluates crypto asset volatility and network activity growth.
    """
    annual_vol = round(daily_volatility_pct * (365.0 ** 0.5) * 100.0, 2)

    if annual_vol >= 80.0:
        regime = "Extreme Volatility (High Risk Speculation)"
    elif annual_vol >= 40.0:
        regime = "High Volatility (Growth Asset)"
    else:
        regime = "Moderate Volatility (Stable Growth)"

    return {
        "asset": asset_name.upper(),
        "price_usd": price,
        "daily_volatility_pct": daily_volatility_pct * 100.0,
        "annualized_volatility_pct": annual_vol,
        "hash_rate_growth_pct": hash_rate_growth_pct * 100.0,
        "volatility_regime": regime,
    }
