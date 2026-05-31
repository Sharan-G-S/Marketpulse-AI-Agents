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

    # Map current holdings by upper ticker for quick lookup
    current_holdings = {}
    prices = {}
    for h in holdings:
        ticker = str(h.get("ticker", "")).upper()
        if ticker:
            current_holdings[ticker] = max(0.0, float(h.get("market_value", 0.0) or 0.0))
            prices[ticker] = max(0.0, float(h.get("price", 0.0) or 0.0))

    # All tickers present in either target_allocations or current_holdings
    all_tickers = sorted(list(set(normalized_targets.keys()) | set(current_holdings.keys())))

    positions_report = []
    for ticker in all_tickers:
        cur_val = current_holdings.get(ticker, 0.0)
        tgt_weight = normalized_targets.get(ticker, 0.0)
        tgt_val = round(tgt_weight * total_value, 2)
        cur_weight = round(cur_val / total_value, 4) if total_value > 0 else 0.0
        diff_val = round(cur_val - tgt_val, 2)
        diff_pct = round(cur_weight - tgt_weight, 4)


