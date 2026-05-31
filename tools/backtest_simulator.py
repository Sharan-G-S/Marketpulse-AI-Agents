"""
Crossover Backtest Simulator for MarketPulse.

Simulates trading a fast/slow moving average crossover strategy on historical prices.
Starting with a base capital, it tracks transactions, cash, and portfolio equity.

No LLM required — pure mathematical simulation.
"""

from typing import Any, Dict, List

from tools.ma_crossover import compute_ema, compute_sma, extract_closes


def run_crossover_backtest(  # noqa: C901
    price_history: List[Dict[str, Any]],
    fast_period: int = 50,
    slow_period: int = 200,
    initial_capital: float = 10000.0,
    use_ema: bool = False,
) -> Dict[str, Any]:
    """
    Simulate a moving average crossover strategy on historical prices.

    Args:
        price_history: List of OHLCV bar dicts, oldest first.
        fast_period: Short MA window (default 50).
        slow_period: Long MA window (default 200).
        initial_capital: Starting cash balance in dollars (default 10,000).
        use_ema: If True, use EMA instead of SMA.

    Returns:
        Dict with backtest details and summary metrics.
    """
    closes = extract_closes(price_history)
    ma_type = "EMA" if use_ema else "SMA"

    # Edge case: insufficient prices
    if len(closes) < slow_period + 1:
        return {
            "initial_capital": initial_capital,
            "final_value": initial_capital,
            "total_return_pct": 0.0,
            "benchmark_return_pct": 0.0,
            "trades_count": 0,
            "win_rate_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "trades": [],
            "status": "Insufficient Data",
        }

    ma_fn = compute_ema if use_ema else compute_sma
    fast_series = ma_fn(closes, fast_period)
    slow_series = ma_fn(closes, slow_period)

    cash = initial_capital
    shares = 0.0
    position_active = False
    trades: List[Dict[str, Any]] = []
    portfolio_values: List[float] = []

    # Get dates if available, otherwise use index
    dates = [
        str(r.get("date") or r.get("Date") or r.get("timestamp") or idx)
        for idx, r in enumerate(price_history)
    ]

    # Pre-populate portfolio value for initial period
    for i in range(slow_period):
        portfolio_values.append(initial_capital)

    for i in range(slow_period, len(closes)):
        price = closes[i]
        date_str = dates[i]

        f_prev, f_curr = fast_series[i - 1], fast_series[i]
        s_prev, s_curr = slow_series[i - 1], slow_series[i]

        # Standard crossovers
        if f_prev is not None and s_prev is not None and f_curr is not None and s_curr is not None:
            was_below = f_prev < s_prev
            now_above = f_curr > s_curr
            was_above = f_prev > s_prev
            now_below = f_curr < s_curr

            if was_below and now_above and not position_active:
                # Buy signal
                shares = cash / price if price > 0.0 else 0.0
                cash = 0.0
                position_active = True
                trades.append({
                    "type": "BUY",
                    "date": date_str,
                    "price": price,
                    "shares": shares,
                    "cash_after": cash,
                })
            elif was_above and now_below and position_active:
                # Sell signal
                cash = shares * price
                shares = 0.0
                position_active = False
                trades[-1]["sell_date"] = date_str
                trades[-1]["sell_price"] = price
                p_buy = trades[-1]["price"]
                trades[-1]["return_pct"] = round((price - p_buy) / p_buy * 100, 2) if p_buy > 0.0 else 0.0
                trades[-1]["cash_after"] = cash

        current_value = cash + (shares * price)
        portfolio_values.append(current_value)

    # Final calculations
    final_value = portfolio_values[-1]
    total_return_pct = round((final_value - initial_capital) / initial_capital * 100, 2)

    # Benchmark: buy and hold starting from the first tradable bar (slow_period)
    bench_start = closes[slow_period]
    bench_end = closes[-1]
    benchmark_return_pct = round((bench_end - bench_start) / bench_start * 100, 2) if bench_start != 0 else 0.0

    # Win rate
    closed_trades = [t for t in trades if "sell_price" in t]
    wins = sum(1 for t in closed_trades if t.get("return_pct", 0.0) > 0)
    win_rate_pct = round(wins / len(closed_trades) * 100, 2) if closed_trades else 0.0

    # Max Drawdown
    peak = -99999999.0
    max_dd = 0.0
    for val in portfolio_values:
        if val > peak:
            peak = val
        dd = (val - peak) / peak if peak > 0 else 0.0
        if dd < max_dd:
            max_dd = dd
    max_drawdown_pct = round(max_dd * 100, 2)

    # Sharpe ratio
    daily_returns = []
    for i in range(1, len(portfolio_values)):
        prev = portfolio_values[i - 1]
        curr = portfolio_values[i]
        daily_returns.append((curr - prev) / prev if prev != 0 else 0.0)

    import math
    if len(daily_returns) >= 2:
        mean_ret = sum(daily_returns) / len(daily_returns)
        variance = sum((x - mean_ret) ** 2 for x in daily_returns) / (len(daily_returns) - 1)
        daily_vol = math.sqrt(variance)
        vol = daily_vol * math.sqrt(252)

        # Annualised return (geometric)
        n = len(daily_returns)
        try:
            factor = final_value / initial_capital
            if factor > 0 and n > 0:
                ann_ret = factor ** (252 / n) - 1
            else:
                ann_ret = -1.0
        except Exception:
            ann_ret = 0.0

        rf = 0.05
        sharpe = round((ann_ret - rf) / vol, 4) if vol > 0 else 0.0
    else:
        sharpe = 0.0

    return {
        "ma_type": ma_type,
        "fast_period": fast_period,
        "slow_period": slow_period,
        "initial_capital": initial_capital,
        "final_value": round(final_value, 2),
        "total_return_pct": total_return_pct,
        "benchmark_return_pct": benchmark_return_pct,
        "trades_count": len(trades),
        "win_rate_pct": win_rate_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "sharpe_ratio": sharpe,
        "trades": trades,
        "status": "Success",
    }


def format_backtest_report(result: Dict[str, Any]) -> str:
    """
    Format the backtest result dict as a beautiful Markdown report.

    Args:
        result: Dict returned by run_crossover_backtest.

    Returns:
        Markdown formatted report string.
    """
    status = result.get("status", "Unknown")
    if status == "Insufficient Data":
        return (
            "### 📈 Crossover Backtest Simulation Report\n\n"
            "❌ **Backtest Failed:** Insufficient price history data to run the simulation."
        )

    ma_type = result.get("ma_type", "SMA")
    fast = result.get("fast_period", 50)
    slow = result.get("slow_period", 200)
    init_cap = result.get("initial_capital", 10000.0)
    final_val = result.get("final_value", 10000.0)
    tot_ret = result.get("total_return_pct", 0.0)
    bench_ret = result.get("benchmark_return_pct", 0.0)
    trades_count = result.get("trades_count", 0)
    win_rate = result.get("win_rate_pct", 0.0)
    max_dd = result.get("max_drawdown_pct", 0.0)
    sharpe = result.get("sharpe_ratio", 0.0)

    perf_status = "✅ Outperformed Benchmark" if tot_ret > bench_ret else "❌ Underperformed Benchmark"
    ret_color = "🟢" if tot_ret >= 0 else "🔴"

    lines = [
        "### 📈 Crossover Backtest Simulation Report",
        "",
        f"**Strategy Configuration:** `{ma_type} Crossover ({fast} / {slow})`",
        f"**Performance Status:** {perf_status}",
        "",
        "#### 📊 Performance & Efficiency Metrics",
        f"- **Initial Capital:** `${init_cap:,.2f}`",
        f"- **Final Portfolio Value:** `${final_val:,.2f}`",
        f"- **Total Strategy Return:** {ret_color} `{tot_ret:+.2f}%`",
        f"- **Benchmark Return (Buy & Hold):** `{bench_ret:+.2f}%`",
        f"- **Strategy Annualised Sharpe Ratio:** `{sharpe:.4f}`",
        f"- **Maximum Portfolio Drawdown:** `{max_dd:.2f}%`",
        "",
        "#### 🔄 Trade Activity Summary",
        f"- **Total Executed Trades:** `{trades_count}`",
        f"- **Strategy Win Rate:** `{win_rate:.2f}%`",
        "",
    ]

    trades = result.get("trades", [])
    if not trades:
        lines.append("_No trades were executed during the backtest window._")
    else:
        lines.extend([
            "#### 📝 Transaction Ledger (Chronological)",
            "",
            "| Trade # | Buy Date | Buy Price | Sell Date | Sell Price | Return % | Cash After |",
            "|---------|----------|-----------|-----------|------------|----------|------------|",
        ])
        for idx, t in enumerate(trades, 1):
            sell_date = t.get("sell_date", "ACTIVE")
            sell_price = f"${t['sell_price']:.2f}" if "sell_price" in t else "—"
            ret_str = f"{t['return_pct']:+.2f}%" if "return_pct" in t else "—"
            cash_after = f"${t['cash_after']:,.2f}" if t.get("cash_after", 0.0) > 0 else "—"
            lines.append(
                f"| {idx} "
                f"| {t['date']} "
                f"| ${t['price']:.2f} "
                f"| {sell_date} "
                f"| {sell_price} "
                f"| {ret_str} "
                f"| {cash_after} |"
            )

    return "\n".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "run_crossover_backtest",
    "format_backtest_report",
]

_MODULE = "tools/backtest_simulator"
_VERSION = "1.8.0"
