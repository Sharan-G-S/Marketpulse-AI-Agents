"""
MarketPulse — Beta Hedging & Delta Neutral Calculator
Calculates index short contracts/shares required to hedge portfolio market exposure.
"""

from typing import Any, Dict


def calculate_beta_hedge(
    portfolio_value: float,
    portfolio_beta: float = 1.2,
    index_price: float = 500.0,
) -> Dict[str, Any]:
    """
    Computes required index short position to achieve delta neutrality.

    Args:
        portfolio_value: Total portfolio market value
        portfolio_beta: Weighted portfolio beta
        index_price: Index price (e.g. SPY price $500)

    Returns:
        Dict with hedge_value_required, index_shares_to_short, and market_exposure.
    """
    if not portfolio_value or portfolio_value <= 0 or not index_price or index_price <= 0:
        return {"error": "Invalid inputs for beta hedging."}

    b = max(0.0, portfolio_beta)
    hedge_required = portfolio_value * b
    shares_to_short = hedge_required / index_price

    return {
        "portfolio_value": portfolio_value,
        "portfolio_beta": b,
        "hedge_value_required": round(float(hedge_required), 2),
        "index_shares_to_short": round(float(shares_to_short), 2),
        "net_beta_after_hedge": 0.0,
    }
