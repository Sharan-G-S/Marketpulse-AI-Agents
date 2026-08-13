"""
Portfolio Performance Tracker for MarketPulse.

Computes P&L, weight, and return metrics for a user-defined portfolio
of stock positions with NoneType safety guards.
"""

from typing import Any, Dict, List, Optional, Tuple

Position = Dict[str, Any]
PositionResult = Dict[str, Any]
PortfolioSummary = Dict[str, Any]


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely cast value to float handling None, empty strings, and bad types."""
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def compute_position(
    position: Position,
    current_price: float,
    total_market_value: float = 0.0,
) -> PositionResult:
    """
    Compute derived metrics for a single portfolio position with NoneType safety.
    """
    qty = _safe_float(position.get("qty") or position.get("shares"), 0.0)
    avg_cost = _safe_float(position.get("avg_cost") or position.get("cost_price"), 0.0)
    price = _safe_float(current_price, 0.0)
    ticker = str(position.get("ticker", "")).upper()

    market_value = qty * price
    cost_basis = qty * avg_cost
    unrealised_pl = market_value - cost_basis

    unrealised_pct: Optional[float]
    if avg_cost == 0:
        unrealised_pct = None
    else:
        unrealised_pct = round((price - avg_cost) / avg_cost * 100, 4)

    weight = (market_value / total_market_value * 100) if total_market_value else 0.0

    return {
        "ticker": ticker,
        "qty": qty,
        "avg_cost": avg_cost,
        "current_price": price,
        "market_value": round(market_value, 2),
        "cost_basis": round(cost_basis, 2),
        "unrealised_pl": round(unrealised_pl, 2),
        "unrealised_pct": unrealised_pct,
        "weight_pct": round(weight, 4),
    }


def compute_portfolio(
    positions: List[Position],
    price_map: Optional[Dict[str, float]] = None,
) -> PortfolioSummary:
    """
    Compute the full portfolio summary from a list of positions and live prices.
    """
    if not positions:
        return {
            "total_market_value": 0.0,
            "total_cost_basis": 0.0,
            "total_unrealised_pl": 0.0,
            "total_return_pct": 0.0,
            "best_performer": "—",
            "worst_performer": "—",
            "positions": [],
            "n_positions": 0,
        }

    prices = price_map or {}
    raw_results = []
    for pos in positions:
        ticker = str(pos.get("ticker", "")).upper()
        default_cost = _safe_float(pos.get("avg_cost") or pos.get("cost_price"), 0.0)
        price = _safe_float(prices.get(ticker), default_cost)
        raw_results.append((pos, price))

    total_mv = sum(_safe_float(p.get("qty") or p.get("shares"), 0.0) * price for p, price in raw_results)

    results: List[PositionResult] = []
    for pos, price in raw_results:
        results.append(compute_position(pos, price, total_market_value=total_mv))

    total_cost = sum(r["cost_basis"] for r in results)
    total_pl = sum(r["unrealised_pl"] for r in results)
    total_ret = ((total_mv - total_cost) / total_cost * 100) if total_cost else 0.0

    sorted_by_pct = sorted(results, key=lambda r: (r["unrealised_pct"] or 0.0))
    best = sorted_by_pct[-1]["ticker"] if results else "—"
    worst = sorted_by_pct[0]["ticker"] if results else "—"

    return {
        "total_market_value": round(total_mv, 2),
        "total_cost_basis": round(total_cost, 2),
        "total_unrealised_pl": round(total_pl, 2),
        "total_return_pct": round(total_ret, 4),
        "best_performer": best,
        "worst_performer": worst,
        "positions": results,
        "n_positions": len(results),
    }


def top_holdings(
    summary: PortfolioSummary,
    n: int = 5,
) -> List[PositionResult]:
    return sorted(
        summary.get("positions", []),
        key=lambda r: r["market_value"],
        reverse=True,
    )[:n]


def sector_allocation(
    positions: List[PositionResult],
    sector_map: Optional[Dict[str, str]] = None,
) -> Dict[str, float]:
    sm = sector_map or {}
    allocation: Dict[str, float] = {}
    for p in positions:
        sector = sm.get(p["ticker"], "Other")
        allocation[sector] = allocation.get(sector, 0.0) + p["market_value"]
    return allocation


__all__ = [
    "compute_position",
    "compute_portfolio",
    "top_holdings",
    "sector_allocation",
]
