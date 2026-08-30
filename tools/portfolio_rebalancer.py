"""
MarketPulse — Autonomous Portfolio Rebalancing Engine
Calculates trade orders required to re-align actual portfolio weights to target model weights.
"""

from typing import Any, Dict, List


def compute_portfolio_rebalancing(
    holdings: List[Dict[str, Any]],
    target_weights: Dict[str, float],
) -> Dict[str, Any]:
    """
    Computes portfolio rebalancing actions and weight deviations.
    """
    if not holdings:
        return {
            "total_value": 0.0,
            "target_deviation_mad_pct": 100.0,
            "positions": [],
            "rebalance_actions": [],
        }

    # Normalize target weights
    total_target = sum(target_weights.values())
    norm_targets = {}
    if total_target > 0:
        for t, w in target_weights.items():
            norm_targets[t] = w / total_target
    else:
        norm_targets = target_weights

    # Compute current total market value
    total_val = 0.0
    valid_positions = []
    for h in holdings:
        ticker = h.get("ticker", "").upper()
        qty = max(0.0, float(h.get("qty", 0.0) or 0.0))
        price = max(0.0, float(h.get("price", 0.0) or 0.0))
        mv = max(0.0, float(h.get("market_value", 0.0) or (qty * price)))
        total_val += mv
        valid_positions.append({
            "ticker": ticker,
            "qty": qty,
            "price": price,
            "current_value": mv,
        })

    if total_val <= 0:
        return {
            "total_value": 0.0,
            "target_deviation_mad_pct": 100.0 if holdings else 0.0,
            "positions": [
                {
                    "ticker": p["ticker"],
                    "current_value": p["current_value"],
                    "current_weight": 0.0,
                    "target_weight": norm_targets.get(p["ticker"], 0.0),
                    "deviation_pct": -norm_targets.get(p["ticker"], 0.0),
                    "target_value": 0.0,
                }
                for p in valid_positions
            ],
            "rebalance_actions": [],
        }

    positions = []
    actions = []
    abs_deviations = []

    for p in valid_positions:
        ticker = p["ticker"]
        cur_val = p["current_value"]
        price = p["price"]
        cur_weight = cur_val / total_val
        t_weight = norm_targets.get(ticker, 0.0)
        t_val = total_val * t_weight
        dev = cur_weight - t_weight

        abs_deviations.append(abs(dev))

        positions.append({
            "ticker": ticker,
            "current_value": cur_val,
            "current_weight": cur_weight,
            "target_weight": t_weight,
            "deviation_pct": dev,
            "target_value": t_val,
        })

        diff_val = t_val - cur_val
        if abs(diff_val) > 0.01:
            act_type = "BUY" if diff_val > 0 else "SELL"
            amount = abs(diff_val)
            shares = amount / price if price > 0 else 0.0
            actions.append({
                "ticker": ticker,
                "action": act_type,
                "amount": amount,
                "shares": shares,
            })

    mad = (sum(abs_deviations) / len(abs_deviations)) if abs_deviations else 0.0

    return {
        "total_value": total_val,
        "target_deviation_mad_pct": round(mad * 100.0, 2),
        "positions": positions,
        "rebalance_actions": actions,
    }


def calculate_portfolio_rebalance_orders(
    positions: List[Dict[str, Any]],
    target_weights: Dict[str, float],
    total_cash_available: float = 0.0,
) -> Dict[str, Any]:
    """Alias function for new tool format."""
    res = compute_portfolio_rebalancing(positions, target_weights)
    return {
        "total_portfolio_value": res["total_value"],
        "trade_orders": res["rebalance_actions"],
        "rebalance_status": "Rebalance Trades Generated",
    }


def format_rebalance_report(rebalance_res: Dict[str, Any]) -> str:
    """Formats rebalancing results as Markdown summary."""
    if not rebalance_res or not rebalance_res.get("positions"):
        return "Portfolio Rebalancing Skipped — Empty Holdings or Total Value $0.00."

    lines = [
        f"# Portfolio Rebalancing Analysis",
        f"**Total Portfolio Value**: ${rebalance_res.get('total_value', 0):,.2f}",
        f"**Mean Absolute Deviation (MAD)**: {rebalance_res.get('target_deviation_mad_pct', 0):.2f}%\n",
        "### Recommended Rebalance Actions:",
    ]
    actions = rebalance_res.get("rebalance_actions", [])
    if not actions:
        lines.append("- Portfolio is perfectly aligned with target weights. No trades needed.")
    else:
        for a in actions:
            lines.append(f"- **{a['ticker']}**: {a['action']} ${a['amount']:,.2f} ({a['shares']:.2f} shares)")

    return "\n".join(lines)
