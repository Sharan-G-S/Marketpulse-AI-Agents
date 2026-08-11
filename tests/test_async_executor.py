"""
Unit tests for tools/async_executor.py
"""

import time
from tools.async_executor import run_batch_parallel


def mock_fetch(ticker: str):
    time.sleep(0.05)
    return {"ticker": ticker, "status": "ok"}


def test_run_batch_parallel():
    items = ["AAPL", "TSLA", "NVDA", "MSFT"]
    t0 = time.time()
    results = run_batch_parallel(mock_fetch, items, max_workers=4)
    dt = time.time() - t0

    assert len(results) == 4
    assert "AAPL" in results
    assert results["AAPL"]["status"] == "ok"
    # Concurrent execution should take ~0.05-0.15s, much less than sequential 0.20s
    assert dt < 0.20
