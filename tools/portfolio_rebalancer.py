"""
Portfolio Allocation and Rebalancing Engine for MarketPulse.

Calculates current position deviations from a user-defined target allocation,
and computes trade instructions (buys/sells) to rebalance the portfolio.

No LLM required — pure mathematics.
"""

from typing import Any, Dict, List, Optional


def compute_portfolio_rebalancing(
    holdings: List[Dict[str, Any]],
    target_allocations: Dict[str, float],
) -> Dict[str, Any]:
    """
    Computes rebalancing trade operations to match the specified target allocation.

    Args:
        holdings: List of position dicts, each containing:
            - 'ticker': str (e.g. 'AAPL')
            - 'market_value': float (total current dollar value)
            - 'price': float (current share price)
        target_allocations: Dict mapping ticker (uppercase) to target weight fraction (0.0 to 1.0).

    Returns:
        Dict with portfolio rebalancing results, metrics, and suggestions.
    """
    if not target_allocations:
        return {
            "total_value": 0.0,
            "target_deviation_mad": 0.0,
            "positions": [],
            "rebalance_actions": [],
            "status": "No Targets Provided",
        }

    # Normalize target weights to ensure they sum to exactly 1.0
    targets = {str(k).upper(): float(v) for k, v in target_allocations.items() if v > 0}
    total_target_weight = sum(targets.values())
    if total_target_weight == 0:
        return {
            "total_value": 0.0,
            "target_deviation_mad": 0.0,
            "positions": [],
            "rebalance_actions": [],
            "status": "Invalid Target Weights",
        }
    normalized_targets = {k: v / total_target_weight for k, v in targets.items()}

    # Calculate total portfolio value
    total_value = sum(max(0.0, float(h.get("market_value", 0.0) or 0.0)) for h in holdings)

