"""
Crossover Backtest Simulator for MarketPulse.

Simulates trading a fast/slow moving average crossover strategy on historical prices.
Starting with a base capital, it tracks transactions, cash, and portfolio equity.

No LLM required — pure mathematical simulation.
"""

from typing import Any, Dict, List, Optional

from tools.ma_crossover import compute_ema, compute_sma, extract_closes


def run_crossover_backtest(
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
                shares = cash / price
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
                trades[-1]["return_pct"] = round((price - trades[-1]["price"]) / trades[-1]["price"] * 100, 2)
                trades[-1]["cash_after"] = cash

        current_value = cash + (shares * price)
        portfolio_values.append(current_value)


