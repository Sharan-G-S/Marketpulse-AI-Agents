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

        # Determine trade actions
        action = "HOLD"
        shares_to_trade = 0.0
        price = prices.get(ticker, 0.0)

        # Threshold to avoid trivial trades (e.g. less than $1.00 deviation)
        if abs(diff_val) >= 1.0:
            if diff_val > 0:
                action = "SELL"
            else:
                action = "BUY"

            if price > 0:
                shares_to_trade = round(abs(diff_val) / price, 4)

        positions_report.append({
            "ticker": ticker,
            "current_value": cur_val,
            "current_weight": cur_weight,
            "target_weight": tgt_weight,
            "target_value": tgt_val,
            "deviation_value": diff_val,
            "deviation_pct": diff_pct,
            "action": action,
            "amount": abs(diff_val),
            "shares": shares_to_trade,
            "price": price,
        })

    # Calculate Mean Absolute Deviation (MAD) of weights
    if positions_report:
        mad = sum(abs(p["deviation_pct"]) for p in positions_report) / len(positions_report)
        mad_pct = round(mad * 100, 2)
    else:
        mad_pct = 0.0

    rebalance_actions = [p for p in positions_report if p["action"] != "HOLD"]

    return {
        "total_value": round(total_value, 2),
        "target_deviation_mad_pct": mad_pct,
        "positions": positions_report,
        "rebalance_actions": rebalance_actions,
        "status": "Success",
    }


def format_rebalance_report(result: Dict[str, Any]) -> str:
    """
    Format the rebalancing result dict as a beautiful Markdown dashboard.

    Args:
        result: Dict returned by compute_portfolio_rebalancing.

    Returns:
        Markdown formatted report string.
    """
    status = result.get("status", "Unknown")
    if status == "No Targets Provided":
        return (
            "### ⚖️ Portfolio Rebalancing Analysis\n\n"
            "❌ **Rebalancing Skipped:** No target allocations were provided."
        )
    if status == "Invalid Target Weights":
        return (
            "### ⚖️ Portfolio Rebalancing Analysis\n\n"
            "❌ **Rebalancing Skipped:** Provided target weights are invalid or sum to zero."
        )

    total_value = result.get("total_value", 0.0)
    mad_pct = result.get("target_deviation_mad_pct", 0.0)
    positions = result.get("positions", [])
    actions = result.get("rebalance_actions", [])

    if mad_pct < 1.0:
        health_status = "🟢 Perfectly Balanced (MAD < 1%)"
    elif mad_pct < 5.0:
        health_status = "🟡 Slight Deviation (MAD < 5%)"
    else:
        health_status = "🔴 Significant Rebalancing Required (MAD ≥ 5%)"

    lines = [
        "### ⚖️ Portfolio Rebalancing Analysis",
        "",
        f"**Portfolio Alignment Status:** {health_status}",
        f"**Total Portfolio Value:** `${total_value:,.2f}`  |  **Mean Absolute Deviation (MAD):** `{mad_pct:.2f}%`",
        "",
        "#### 📊 Current vs. Target Allocations",
        "",
        "| Ticker | Current Value | Current Weight | Target Weight | Target Value | Deviation ($) | Deviation (%) |",
        "|--------|---------------|----------------|---------------|--------------|---------------|---------------|",
    ]

    for p in positions:
        cur_val = f"${p['current_value']:,.2f}"
        tgt_val = f"${p['target_value']:,.2f}"
        cur_w = f"{p['current_weight']*100:.2f}%"
        tgt_w = f"{p['target_weight']*100:.2f}%"

        diff_val = p['deviation_value']
        diff_val_str = f"+${diff_val:,.2f}" if diff_val >= 0 else f"-${abs(diff_val):,.2f}"
        diff_pct = p['deviation_pct'] * 100
        diff_pct_str = f"+{diff_pct:.2f}%" if diff_pct >= 0 else f"{diff_pct:.2f}%"

        lines.append(
            f"| `{p['ticker']}` "
            f"| {cur_val} "
            f"| {cur_w} "
            f"| {tgt_w} "
            f"| {tgt_val} "
            f"| {diff_val_str} "
            f"| {diff_pct_str} |"
        )

    lines.append("")
    lines.append("#### 🛠️ Recommended Rebalancing Actions")
    lines.append("")

    if not actions:
        lines.append("_Portfolio is aligned with targets. No rebalancing trades required._")
    else:
        lines.extend([
            "| Action | Ticker | Trade Amount | Est. Shares | Share Price |",
            "|--------|--------|--------------|-------------|-------------|",
        ])
        for a in actions:
            action_badge = "🟢 BUY" if a["action"] == "BUY" else "🔴 SELL"
            shares_str = f"{a['shares']:.4f}" if a["shares"] > 0 else "—"
            price_str = f"${a['price']:.2f}" if a["price"] > 0 else "—"
            lines.append(
                f"| {action_badge} "
                f"| `{a['ticker']}` "
                f"| ${a['amount']:,.2f} "
                f"| {shares_str} "
                f"| {price_str} |"
            )

    return "\n".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_portfolio_rebalancing",
    "format_rebalance_report",
]

_MODULE = "tools.portfolio_rebalancer"
_VERSION = "1.9.0"






