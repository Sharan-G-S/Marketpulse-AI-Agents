"""
MarketPulse — Pipeline Pre-Fetcher Engine
Pre-fetches stock quote summaries and news articles in parallel background threads.
"""

from typing import Any, Dict, List
from tools.async_executor import run_batch_parallel
from tools.stock_tools import get_stock_summary


def prefetch_ticker_batch(tickers: List[str]) -> Dict[str, Any]:
    """
    Pre-fetches stock summaries for a list of tickers concurrently.
    """
    if not tickers:
        return {}

    def _fetch_safe(t: str):
        try:
            return get_stock_summary.invoke({"ticker": t})
        except Exception as e:
            return {"ticker": t, "error": str(e)}

    return run_batch_parallel(_fetch_safe, tickers, max_workers=5)
