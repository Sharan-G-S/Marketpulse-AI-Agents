"""
Portfolio Tracker for MarketPulse

Accepts a portfolio of stock positions (ticker, quantity, average buy price)
and computes real-time P&L, sector allocation, diversification score,
and a portfolio health summary — all without requiring an LLM call.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from graph.state import MarketPulseState
from tools.stock_tools import get_stock_summary

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

Position = Dict[str, Any]
"""
A single portfolio position:
    {
        "ticker":      str,       e.g. "AAPL"
        "quantity":    float,     e.g. 10.0
        "avg_price":   float,     e.g. 150.00   (average buy price per share)
        "sector":      str,       e.g. "Technology"   (optional)
    }
"""

PortfolioResult = Dict[str, Any]


# ---------------------------------------------------------------------------
# Portfolio computation helpers
# ---------------------------------------------------------------------------


def compute_position_pnl(
    position: Position,
    current_price: float,
) -> Dict[str, float]:
    """
    Compute unrealised P&L for a single position.

    Args:
        position:      Position dict with ticker, quantity, avg_price.
        current_price: Current market price per share.

    Returns:
        Dict with cost_basis, market_value, unrealised_pnl, pnl_pct, weight (stub).
    """
    qty = float(position.get("quantity", 0))
    avg = float(position.get("avg_price", 0))

    cost_basis = round(qty * avg, 2)
    market_value = round(qty * current_price, 2)
    unrealised_pnl = round(market_value - cost_basis, 2)
    pnl_pct = round(((current_price - avg) / avg) * 100, 2) if avg > 0 else 0.0

    return {
        "cost_basis": cost_basis,
        "market_value": market_value,
        "unrealised_pnl": unrealised_pnl,
        "pnl_pct": pnl_pct,
    }


def compute_sector_allocation(positions: List[Position]) -> Dict[str, float]:
    """
    Compute portfolio sector weights from a list of positions with market values.

    Each position must contain 'market_value' and optionally 'sector'.
    Returns a dict mapping sector name → percentage weight.
    """
    total = sum(p.get("market_value", 0.0) for p in positions)
    if total == 0:
        return {}

    sector_totals: Dict[str, float] = {}
    for p in positions:
        sector = p.get("sector") or "Unknown"
        sector_totals[sector] = sector_totals.get(sector, 0.0) + p.get("market_value", 0.0)

    return {s: round((v / total) * 100, 2) for s, v in sector_totals.items()}


def compute_diversification_score(sector_allocation: Dict[str, float]) -> float:
    """
    Compute a diversification score from 0 to 100.

    Uses a Herfindahl-Hirschman Index (HHI) approach — lower concentration
    → higher score. Score = 100 * (1 - HHI_normalised).

    100 = perfectly equal weights across sectors.
    0   = fully concentrated in a single sector.
    """
    if not sector_allocation:
        return 0.0

    n = len(sector_allocation)
    if n == 1:
        # Fully concentrated in a single sector — lowest possible score
        return 0.0

    weights = [w / 100.0 for w in sector_allocation.values()]
    hhi = sum(w**2 for w in weights)

    # HHI ranges from 1/n (perfect diversity) to 1 (total concentration).
    min_hhi = 1.0 / n
    normalised = (hhi - min_hhi) / (1 - min_hhi) if (1 - min_hhi) > 0 else 0.0
    score = round((1 - normalised) * 100, 1)
    return max(0.0, min(100.0, score))


def classify_diversification(score: float) -> str:
    """Classify diversification score into a human-readable label."""
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Fair"
    return "Poor"


def compute_portfolio_beta(positions: List[Position]) -> Optional[float]:
    """
    Compute weighted average portfolio beta.

    Positions must contain 'market_value' and optionally 'beta'.
    Returns None if no beta data is available.
    """
    total_value = sum(p.get("market_value", 0.0) for p in positions)
    if total_value == 0:
        return None

    weighted_beta = 0.0
    has_any = False
    for p in positions:
        beta = p.get("beta")
        if beta is not None:
            weighted_beta += (p.get("market_value", 0.0) / total_value) * float(beta)
            has_any = True

    return round(weighted_beta, 3) if has_any else None


def identify_top_performers(
    positions: List[Position],
    n: int = 3,
) -> Tuple[List[Position], List[Position]]:
    """
    Return the top-n gainers and top-n losers from a list of positions.

    Positions must have a 'pnl_pct' key.
    Returns (gainers, losers) — each sorted by pnl_pct descending/ascending.
    """
    sorted_pos = sorted(positions, key=lambda p: p.get("pnl_pct", 0.0), reverse=True)
    gainers = [p for p in sorted_pos if p.get("pnl_pct", 0.0) >= 0][:n]
    losers = sorted(
        [p for p in positions if p.get("pnl_pct", 0.0) < 0],
        key=lambda p: p.get("pnl_pct", 0.0),
    )[:n]
    return gainers, losers


# ---------------------------------------------------------------------------
# Main portfolio analysis function
# ---------------------------------------------------------------------------


def analyse_portfolio(
    positions: List[Position],
    price_lookup: Dict[str, Dict[str, Any]],
) -> PortfolioResult:
    """
    Run a full portfolio analysis given positions and current price data.

    Args:
        positions:    List of Position dicts (ticker, quantity, avg_price, sector).
        price_lookup: Dict mapping ticker -> stock_summary dict (must have
                      'current_price' and optionally 'beta', 'sector').

    Returns:
        PortfolioResult dict containing:
            - total_cost_basis
            - total_market_value
            - total_unrealised_pnl
            - total_pnl_pct
            - positions            (enriched list)
            - sector_allocation    (dict: sector -> weight %)
            - diversification_score
            - diversification_label
            - portfolio_beta
            - top_gainers          (list)
            - top_losers           (list)
            - health_summary       (str)
            - generated_at         (ISO-8601 timestamp)
    """
    if not positions:
        return {"error": "No positions provided.", "generated_at": datetime.now(timezone.utc).isoformat()}

    enriched: List[Position] = []

    for raw in positions:
        ticker = raw.get("ticker", "").upper()
        price_data = price_lookup.get(ticker, {})
        current_price = price_data.get("current_price")

        if current_price is None:
            # Skip positions with no price data but mark them
            enriched.append({
                **raw,
                "ticker": ticker,
                "current_price": None,
                "cost_basis": None,
                "market_value": 0.0,
                "unrealised_pnl": None,
                "pnl_pct": None,
                "sector": raw.get("sector") or price_data.get("sector", "Unknown"),
                "beta": price_data.get("beta"),
                "error": "Price data unavailable",
            })
            continue

        pnl = compute_position_pnl(raw, current_price)
        enriched.append({
            **raw,
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "sector": raw.get("sector") or price_data.get("sector", "Unknown"),
            "beta": price_data.get("beta"),
            **pnl,
        })

    # Totals
    valid = [p for p in enriched if p.get("market_value") is not None and p.get("cost_basis") is not None]
    total_cost = round(sum(p["cost_basis"] for p in valid), 2)
    total_value = round(sum(p["market_value"] for p in valid), 2)
    total_pnl = round(total_value - total_cost, 2)
    total_pnl_pct = round(((total_value - total_cost) / total_cost) * 100, 2) if total_cost > 0 else 0.0

    # Sector allocation
    sector_alloc = compute_sector_allocation(valid)
    div_score = compute_diversification_score(sector_alloc)
    div_label = classify_diversification(div_score)

    # Beta
    port_beta = compute_portfolio_beta(valid)

    # Performers
    gainers, losers = identify_top_performers(valid)

    # Health summary
    health = _build_health_summary(
        total_pnl_pct=total_pnl_pct,
        div_label=div_label,
        port_beta=port_beta,
        n_positions=len(valid),
    )

    return {
        "total_cost_basis": total_cost,
        "total_market_value": total_value,
        "total_unrealised_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "positions": enriched,
        "sector_allocation": sector_alloc,
        "diversification_score": div_score,
        "diversification_label": div_label,
        "portfolio_beta": port_beta,
        "top_gainers": [{"ticker": p["ticker"], "pnl_pct": p["pnl_pct"]} for p in gainers],
        "top_losers": [{"ticker": p["ticker"], "pnl_pct": p["pnl_pct"]} for p in losers],
        "health_summary": health,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Agent wrapper for LangGraph integration
# ---------------------------------------------------------------------------


def portfolio_agent(state: MarketPulseState) -> MarketPulseState:
    """
    Portfolio Tracker Agent Node.

    Enriches the shared state with portfolio analytics when positions
    are provided. If no positions exist, the agent is a no-op.
    """
    positions = state.get("portfolio_positions", [])
    if not positions:
        return {
            **state,
            "portfolio_summary": {},
            "portfolio_done": True,
            "messages": state.get("messages", []) + ["[Portfolio Agent] No positions provided; skipped."],
        }

    tickers = sorted({p.get("ticker", "").upper() for p in positions if p.get("ticker")})
    price_lookup: Dict[str, Dict[str, Any]] = {}

    for t in tickers:
        try:
            price_lookup[t] = get_stock_summary.invoke({"ticker": t})
        except Exception as e:
            price_lookup[t] = {"error": str(e)}

    summary = analyse_portfolio(positions, price_lookup)

    return {
        **state,
        "portfolio_summary": summary,
        "portfolio_done": True,
        "messages": state.get("messages", []) + [
            f"[Portfolio Agent] Analysed {len(positions)} positions across {len(tickers)} tickers."
        ],
    }


def _build_health_summary(
    total_pnl_pct: float,
    div_label: str,
    port_beta: Optional[float],
    n_positions: int,
) -> str:
    """Generate a plain-text portfolio health summary string."""
    lines = ["Portfolio Health Summary", "-" * 32]

    # Overall P&L
    if total_pnl_pct >= 10:
        lines.append(f"Performance : Excellent (+{total_pnl_pct:.1f}% unrealised gain)")
    elif total_pnl_pct >= 0:
        lines.append(f"Performance : Positive (+{total_pnl_pct:.1f}% unrealised gain)")
    elif total_pnl_pct >= -10:
        lines.append(f"Performance : Moderate loss ({total_pnl_pct:.1f}% unrealised)")
    else:
        lines.append(f"Performance : Significant loss ({total_pnl_pct:.1f}% unrealised)")

    # Diversification
    lines.append(f"Diversification : {div_label}")
    if div_label == "Poor":
        lines.append("  -> Consider spreading investments across more sectors.")

    # Beta
    if port_beta is not None:
        if port_beta > 1.5:
            lines.append(f"Risk (Beta) : High ({port_beta:.2f}) — portfolio is more volatile than the market.")
        elif port_beta >= 0.8:
            lines.append(f"Risk (Beta) : Moderate ({port_beta:.2f}) — market-aligned volatility.")
        else:
            lines.append(f"Risk (Beta) : Low ({port_beta:.2f}) — portfolio is less volatile than the market.")

    # Position count
    if n_positions < 5:
        lines.append(f"Holdings : Only {n_positions} positions — consider adding more for diversification.")
    else:
        lines.append(f"Holdings : {n_positions} positions tracked.")

    return "\n".join(lines)
