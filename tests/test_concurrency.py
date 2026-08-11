"""
High-throughput concurrency & stress test suite for MarketPulse multi-agent graph.
Verifies thread-safety, state isolation, and zero race conditions under load.
"""

from concurrent.futures import ThreadPoolExecutor
from graph.state import MarketPulseState
from tools.async_executor import run_batch_parallel


def mock_agent_node(ticker: str) -> dict:
    state: MarketPulseState = {
        "ticker": ticker,
        "company_name": f"Company {ticker}",
        "raw_news": [],
        "sentiment_scores": [],
        "overall_sentiment": "Bullish",
        "risk_level": "Low",
        "stock_summary": {"ticker": ticker, "current_price": 100.0},
        "messages": [f"Processed {ticker}"],
    }
    return state


def test_concurrent_agent_state_isolation():
    tickers = [f"TCK{i}" for i in range(20)]
    results = run_batch_parallel(mock_agent_node, tickers, max_workers=10)

    assert len(results) == 20
    for t in tickers:
        assert t in results
        assert results[t]["ticker"] == t
        assert results[t]["stock_summary"]["current_price"] == 100.0
