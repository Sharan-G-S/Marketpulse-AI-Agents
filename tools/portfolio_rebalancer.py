"""
MarketPulse — Autonomous Portfolio Rebalancing Engine
Calculates trade orders required to re-align actual portfolio weights to target model weights.
"""

from typing import Any, Dict, List


def calculate_portfolio_rebalance_orders(
    positions: List[Dict[str, Any]],
    target_weights: Dict[str, float],
    total_cash_available: float = 0.0,
) -> Dict[str, Any]:
    """
    Computes dollar and share trade rebalance actions.
    """
    if not positions:
        return {"error": "No positions provided for rebalancing."}

    total_mv = sum(p.get("market_value", 0.0) for p in positions) + total_cash_available
    if total_mv <= 0:
        return {"error": "Total portfolio value is zero."}

    orders = []
    for pos in positions:
        ticker = pos.get("ticker", "").upper()
        cur_mv = pos.get("market_value", 0.0)
        price = pos.get("current_price", 1.0)
        target_pct = target_weights.get(ticker, 0.0)

        target_mv = total_mv * (target_pct / 100.0)
        diff_mv = target_mv - cur_mv
        diff_shares = round(diff_mv / price, 2) if price > 0 else 0.0

        action = "BUY" if diff_mv > 0 else ("SELL" if diff_mv < 0 else "HOLD")
        orders.append({
            "ticker": ticker,
            "current_weight_pct": round((cur_mv / total_mv) * 100.0, 2),
            "target_weight_pct": target_pct,
            "action": action,
            "dollar_difference": round(abs(diff_mv), 2),
            "shares_difference": abs(diff_shares),
        })

    return {
        "total_portfolio_value": round(total_mv, 2),
        "trade_orders": orders,
        "rebalance_status": "Rebalance Trades Generated",
    }


def compute_portfolio_rebalancing(
    positions: List[Dict[str, Any]],
    target_weights: Dict[str, float],
    total_cash: float = 0.0,
) -> Dict[str, Any]:
    """Alias helper for backward compatibility."""
    return calculate_portfolio_rebalance_orders(positions, target_weights, total_cash)


def format_rebalance_report(rebalance_res: Dict[str, Any]) -> str:
    """Formats rebalancing results as Markdown summary."""
    if "error" in rebalance_res:
        return f"Rebalancing error: {rebalance_res['error']}"

    orders = rebalance_res.get("trade_orders", [])
    lines = [f"# Portfolio Rebalancing Report (Total Value: ${rebalance_res.get('total_portfolio_value', 0):,.2f})\n"]
    for o in orders:
        lines.append(f"- **{o['ticker']}**: {o['action']} ${o['dollar_difference']:,.2f} ({o['shares_difference']} shares)")
    return "\n".join(lines)
