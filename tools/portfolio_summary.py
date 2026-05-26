"""
Portfolio Summary Module for MarketPulse.

Aggregates per-ticker risk metrics into a portfolio-level view,
computing weighted returns, combined volatility, diversification
score, and a colour-coded risk dashboard summary.

No LLM required — pure arithmetic.
"""

from typing import Any, Dict, List


def weighted_portfolio_return(holdings: List[Dict[str, Any]]) -> float:
    """
    Compute the weighted average annualised return of the portfolio.

    Args:
        holdings: List of dicts, each with 'weight' (0-1) and 'ann_return' (decimal).

    Returns:
        Weighted annualised return as a decimal.
    """
    if not holdings:
        return 0.0
    total_weight = sum(h.get("weight", 0) for h in holdings)
    if total_weight == 0:
        return 0.0
    return sum(h.get("weight", 0) * h.get("ann_return", 0) for h in holdings) / total_weight
