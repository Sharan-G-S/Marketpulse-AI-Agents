"""
MarketPulse — Async Parallel Batch Executor Engine
Fetches market data and news for multiple tickers concurrently to cut latency.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List


def run_batch_parallel(
    func: Callable[[str], Any],
    items: List[str],
    max_workers: int = 5,
) -> Dict[str, Any]:
    """
    Executes a synchronous function concurrently across a list of items using ThreadPoolExecutor.

    Args:
        func: Single-item function taking string item (e.g. ticker)
        items: List of string inputs (e.g. tickers)
        max_workers: Concurrent thread limit

    Returns:
        Dict mapping item -> function result or error
    """
    if not items:
        return {}

    results = {}
    with ThreadPoolExecutor(max_workers=min(max_workers, len(items))) as executor:
        futures = {executor.submit(func, item): item for item in items}
        for future in futures:
            item = futures[future]
            try:
                results[item] = future.result()
            except Exception as e:
                results[item] = {"error": str(e), "ticker": item}

    return results
