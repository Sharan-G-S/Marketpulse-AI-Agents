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

