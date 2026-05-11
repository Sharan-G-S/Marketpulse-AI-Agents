"""
Portfolio Performance Tracker for MarketPulse.

Computes P&L, weight, and return metrics for a user-defined portfolio
of stock positions. No LLM required — pure arithmetic.

Terminology:
    position  — one holding: ticker, qty, avg_cost (buy price per share)
    snapshot  — current market price for a ticker
    portfolio — list of positions + current price snapshots
"""

from typing import Any, Dict, List, Optional, Tuple

# ── Type aliases ─────────────────────────────────────────────────────────────

Position = Dict[str, Any]
"""
{
    "ticker":   str,
    "qty":      float,   # number of shares
    "avg_cost": float,   # average buy price per share
}
"""

PositionResult = Dict[str, Any]
"""
{
    "ticker":       str,
    "qty":          float,
    "avg_cost":     float,
    "current_price":float,
    "market_value": float,
    "cost_basis":   float,
    "unrealised_pl":float,
    "unrealised_pct":float,
    "weight_pct":   float,    # % of total portfolio market value
}
"""

PortfolioSummary = Dict[str, Any]
"""
{
    "total_market_value": float,
    "total_cost_basis":   float,
    "total_unrealised_pl":float,
    "total_return_pct":   float,
    "best_performer":     str,
    "worst_performer":    str,
    "positions":          List[PositionResult],
    "n_positions":        int,
}
"""


# ── Core computation ──────────────────────────────────────────────────────────

def compute_position(
    position: Position,
    current_price: float,
    total_market_value: float = 0.0,
) -> PositionResult:
    """
    Compute derived metrics for a single portfolio position.

    Args:
        position:           Dict with ticker, qty, avg_cost.
        current_price:      Live market price for the ticker.
        total_market_value: Portfolio total (for weight calculation).
                            Pass 0.0 to skip weight computation.

    Returns:
        PositionResult dict with all computed fields.
    """
    qty       = float(position.get("qty", 0))
    avg_cost  = float(position.get("avg_cost", 0))
    ticker    = str(position.get("ticker", "")).upper()

    market_value  = qty * current_price
    cost_basis    = qty * avg_cost
    unrealised_pl = market_value - cost_basis
    unrealised_pct = ((current_price - avg_cost) / avg_cost * 100) if avg_cost else 0.0
    weight = (market_value / total_market_value * 100) if total_market_value else 0.0

    return {
        "ticker":         ticker,
        "qty":            qty,
        "avg_cost":       avg_cost,
        "current_price":  current_price,
        "market_value":   round(market_value, 2),
        "cost_basis":     round(cost_basis, 2),
        "unrealised_pl":  round(unrealised_pl, 2),
        "unrealised_pct": round(unrealised_pct, 4),
        "weight_pct":     round(weight, 4),
    }


def compute_portfolio(
    positions: List[Position],
    price_map: Dict[str, float],
) -> PortfolioSummary:
    """
    Compute the full portfolio summary from a list of positions and live prices.

    Args:
        positions: List of Position dicts (ticker, qty, avg_cost).
        price_map: Dict mapping ticker → current market price.

    Returns:
        PortfolioSummary with aggregated metrics and per-position results.
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

    # First pass: compute market values to get total for weight calculation
    raw_results = []
    for pos in positions:
        ticker = str(pos.get("ticker", "")).upper()
        price  = price_map.get(ticker, pos.get("avg_cost", 0.0))
        raw_results.append((pos, float(price)))

    total_mv = sum(float(p.get("qty", 0)) * price for p, price in raw_results)

    # Second pass: compute with weights
    results: List[PositionResult] = []
    for pos, price in raw_results:
        results.append(compute_position(pos, price, total_market_value=total_mv))

    total_cost   = sum(r["cost_basis"] for r in results)
    total_pl     = sum(r["unrealised_pl"] for r in results)
    total_ret    = ((total_mv - total_cost) / total_cost * 100) if total_cost else 0.0

    sorted_by_pct = sorted(results, key=lambda r: r["unrealised_pct"])
    best  = sorted_by_pct[-1]["ticker"] if results else "—"
    worst = sorted_by_pct[0]["ticker"]  if results else "—"

    return {
        "total_market_value":  round(total_mv, 2),
        "total_cost_basis":    round(total_cost, 2),
        "total_unrealised_pl": round(total_pl, 2),
        "total_return_pct":    round(total_ret, 4),
        "best_performer":      best,
        "worst_performer":     worst,
        "positions":           results,
        "n_positions":         len(results),
    }


# ── Allocation helpers ────────────────────────────────────────────────────────

def top_holdings(
    summary: PortfolioSummary,
    n: int = 5,
) -> List[PositionResult]:
    """Return the top-N holdings by market value."""
    return sorted(
        summary.get("positions", []),
        key=lambda r: r["market_value"],
        reverse=True,
    )[:n]


def sector_allocation(
    positions: List[PositionResult],
    sector_map: Optional[Dict[str, str]] = None,
) -> Dict[str, float]:
    """
    Compute market-value allocation by sector.

    Args:
        positions:  List of PositionResult dicts.
        sector_map: Optional dict mapping ticker → sector name.
                    Unknown tickers are grouped under 'Other'.

    Returns:
        Dict mapping sector name → total market value.
    """
    sm = sector_map or {}
    allocation: Dict[str, float] = {}
    for p in positions:
        sector = sm.get(p["ticker"], "Other")
        allocation[sector] = allocation.get(sector, 0.0) + p["market_value"]
    return allocation

# ── Public API ────────────────────────────────────────────────────────────────
__all__ = [
    "compute_position",
    "compute_portfolio",
    "top_holdings",
    "sector_allocation",
]
