"""
pytest configuration - session-level mocks for heavy dependencies.
Mocks yfinance and ddgs so tests run without installing those packages.
"""

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Session-scoped mock of yfinance so tests never need the real package
# ---------------------------------------------------------------------------

def _make_yfinance_mock() -> ModuleType:
    """Build a minimal yfinance stub that satisfies all import-time usage."""
    yf_mock = ModuleType("yfinance")
    ticker_mock = MagicMock()
    ticker_mock.return_value.info = {
        "longName": "Apple Inc.",
        "currentPrice": 188.52,
        "regularMarketPrice": 188.52,
        "previousClose": 185.0,
        "open": 186.0,
        "dayHigh": 190.0,
        "dayLow": 186.0,
        "volume": 65_000_000,
        "averageVolume": 60_000_000,
        "marketCap": 2_900_000_000_000,
        "trailingPE": 28.5,
        "trailingEps": 6.6,
        "fiftyTwoWeekHigh": 199.0,
        "fiftyTwoWeekLow": 150.0,
        "beta": 1.24,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "targetMeanPrice": 210.0,
        "recommendationKey": "buy",
    }
    import pandas as pd

    dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    mock_hist = pd.DataFrame(
        {
            "Open": [100.0, 102.0, 108.0],
            "High": [105.0, 110.0, 112.0],
            "Low": [98.0, 101.0, 106.0],
            "Close": [102.0, 108.0, 115.0],
            "Volume": [1_000_000, 1_200_000, 1_100_000],
        },
        index=dates,
    )
    ticker_mock.return_value.history.return_value = mock_hist
    ticker_mock.return_value.income_stmt = pd.DataFrame()
    yf_mock.Ticker = ticker_mock
    return yf_mock


def _make_ddgs_mock() -> ModuleType:
    """Build a minimal ddgs stub."""
    ddgs_mock = ModuleType("ddgs")
    ddgs_mock.DDGS = MagicMock()
    return ddgs_mock


# Inject mocks before any project module is imported
_YF_MOCK = _make_yfinance_mock()
_DDGS_MOCK = _make_ddgs_mock()

sys.modules.setdefault("yfinance", _YF_MOCK)
sys.modules.setdefault("ddgs", _DDGS_MOCK)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def base_state():
    """Provide a clean base MarketPulseState dict for agent tests."""
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
    """Sample news articles for tests."""
    return [
        {
            "title": "Apple Reports Record Q4 Earnings",
            "description": "Apple exceeded analyst expectations.",
            "source": "Bloomberg",
            "publishedAt": "2025-04-01T10:00:00Z",
            "url": "https://example.com/1",
            "content": "Apple Inc. reported record quarterly revenue...",
        },
        {
            "title": "Apple Faces EU Antitrust Probe",
            "description": "European regulators launch investigation.",
            "source": "Reuters",
            "publishedAt": "2025-04-02T08:00:00Z",
            "url": "https://example.com/2",
            "content": "The European Commission opened a formal investigation...",
        },
    ]


@pytest.fixture
def mock_price_history():
    """Sample OHLCV price history for tests."""
    return [
        {"date": "2025-03-01", "open": 170.0, "high": 175.0, "low": 169.0, "close": 173.0, "volume": 50_000_000},
        {"date": "2025-03-02", "open": 173.0, "high": 178.0, "low": 172.0, "close": 176.0, "volume": 45_000_000},
        {"date": "2025-03-03", "open": 176.0, "high": 182.0, "low": 175.0, "close": 180.0, "volume": 60_000_000},
        {"date": "2025-03-04", "open": 180.0, "high": 185.0, "low": 179.0, "close": 183.0, "volume": 55_000_000},
        {"date": "2025-03-05", "open": 183.0, "high": 190.0, "low": 182.0, "close": 188.0, "volume": 70_000_000},
    ]


@pytest.fixture
def mock_stock_summary():
    """Sample stock summary dict for tests."""
    return {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "current_price": 188.52,
        "previous_close": 185.0,
        "day_high": 190.0,
        "day_low": 186.0,
        "volume": 65_000_000,
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
