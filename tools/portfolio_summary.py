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


def weighted_portfolio_volatility(holdings: List[Dict[str, Any]]) -> float:
    """
    Approximate portfolio volatility as the weighted average of individual
    ticker volatilities (assumes zero cross-correlation — conservative upper bound).

    Args:
        holdings: List of dicts with 'weight' and 'ann_volatility'.

    Returns:
        Weighted volatility as a decimal.
    """
    if not holdings:
        return 0.0
    total_weight = sum(h.get("weight", 0) for h in holdings)
    if total_weight == 0:
        return 0.0
    return sum(h.get("weight", 0) * h.get("ann_volatility", 0) for h in holdings) / total_weight


def worst_drawdown_ticker(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Find the holding with the worst (most negative) max drawdown.

    Returns:
        Dict with 'ticker' and 'max_drawdown' of the worst performer,
        or empty dict if holdings is empty.
    """
    if not holdings:
        return {}
    worst = min(holdings, key=lambda h: h.get("max_drawdown", 0))
    return {"ticker": worst.get("ticker", "N/A"), "max_drawdown": worst.get("max_drawdown", 0)}


def best_sharpe_ticker(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Find the holding with the highest Sharpe ratio.

    Args:
        holdings: List of dicts with 'ticker' and 'sharpe_ratio'.

    Returns:
        Dict with 'ticker' and 'sharpe_ratio' of the best performer,
        or empty dict if holdings is empty.
    """
    if not holdings:
        return {}
    best = max(holdings, key=lambda h: h.get("sharpe_ratio", 0.0))
    return {"ticker": best.get("ticker", "N/A"), "sharpe_ratio": best.get("sharpe_ratio", 0.0)}


def portfolio_risk_label(holdings: List[Dict[str, Any]]) -> str:
    """
    Classify the overall portfolio risk based on the weights and risk labels
    of the individual holdings.

    Args:
        holdings: List of dicts, each with 'weight' (0-1) and 'risk_label' (str).

    Returns:
        One of 'Low', 'Moderate', 'High', 'Very High'.
    """
    if not holdings:
        return "Low"

    label_scores = {
        "Low": 1,
        "Moderate": 2,
        "High": 3,
        "Very High": 4
    }

    total_weight = sum(h.get("weight", 0.0) for h in holdings)
    if total_weight == 0.0:
        scores = [label_scores.get(h.get("risk_label", "Moderate"), 2) for h in holdings]
        avg_score = sum(scores) / len(scores)
    else:
        weighted_score = sum(
            h.get("weight", 0.0) * label_scores.get(h.get("risk_label", "Moderate"), 2)
            for h in holdings
        )
        avg_score = weighted_score / total_weight

    if avg_score >= 3.5:
        return "Very High"
    elif avg_score >= 2.5:
        return "High"
    elif avg_score >= 1.5:
        return "Moderate"
    else:
        return "Low"


