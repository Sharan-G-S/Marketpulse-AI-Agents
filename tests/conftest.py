"""
pytest configuration and shared fixtures for MarketPulse tests.
"""

import os
import sys

import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def base_state():
    """Provide a clean base MarketPulseState for tests."""
    return {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "analysis_depth": "quick",
        "raw_news": [],
        "news_fetched": False,
        "sentiment_scores": [],
        "overall_sentiment": "Neutral",
        "sentiment_confidence": 0.0,
        "sentiment_done": False,
        "stock_summary": {},
        "price_history": [],
        "stock_fetched": False,
        "risk_flags": [],
        "risk_level": "Medium",
        "key_insights": [],
        "risk_done": False,
        "final_report": "",
        "report_path": None,
        "report_done": False,
        "messages": [],
        "error": None,
        "next_agent": "news",
    }


@pytest.fixture
def mock_news():
    """Provide sample news articles for testing."""
    return [
        {
            "title": "Apple Reports Record Q4 Earnings",
            "description": "Apple exceeded analyst expectations with $90B revenue.",
            "source": "Bloomberg",
            "publishedAt": "2025-04-01T10:00:00Z",
            "url": "https://example.com/1",
            "content": "Apple Inc. reported record quarterly revenue...",
        },
        {
            "title": "Apple Faces Antitrust Probe in EU",
            "description": "European regulators launch investigation into App Store practices.",
            "source": "Reuters",
            "publishedAt": "2025-04-02T08:00:00Z",
            "url": "https://example.com/2",
            "content": "The European Commission has opened a formal investigation...",
        },
    ]


@pytest.fixture
def mock_price_history():
    """Provide sample OHLCV price history for testing."""
    return [
        {"date": "2025-03-01", "open": 170.0, "high": 175.0, "low": 169.0, "close": 173.0, "volume": 50000000},
        {"date": "2025-03-02", "open": 173.0, "high": 178.0, "low": 172.0, "close": 176.0, "volume": 45000000},
        {"date": "2025-03-03", "open": 176.0, "high": 182.0, "low": 175.0, "close": 180.0, "volume": 60000000},
        {"date": "2025-03-04", "open": 180.0, "high": 185.0, "low": 179.0, "close": 183.0, "volume": 55000000},
        {"date": "2025-03-05", "open": 183.0, "high": 190.0, "low": 182.0, "close": 188.0, "volume": 70000000},
    ]


@pytest.fixture
def mock_stock_summary():
    """Provide a sample stock summary dict for testing."""
    return {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "current_price": 188.52,
        "previous_close": 185.0,
        "day_high": 190.0,
        "day_low": 186.0,
        "volume": 65000000,
        "market_cap": 2_900_000_000_000,
        "pe_ratio": 28.5,
        "52w_high": 199.0,
        "52w_low": 150.0,
        "beta": 1.24,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "recommendation": "buy",
        "analyst_target_price": 210.0,
        "change_pct": 1.9,
        "trend": "Bullish",
    }
