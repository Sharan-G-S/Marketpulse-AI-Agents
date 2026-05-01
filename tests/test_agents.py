"""
MarketPulse - Unit Tests
All tests are fully mocked - no network calls, no API keys required.
Run with: pytest tests/test_agents.py -v
"""

import os
import sys
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

MOCK_STATE: Dict[str, Any] = {
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
    "watchlist": [],
    "watchlist_done": False,
    "risk_flags": [],
    "risk_level": "Medium",
    "key_insights": [],
    "risk_done": False,
    "portfolio_positions": [],
    "portfolio_summary": {},
    "portfolio_done": False,
    "alerts": [],
    "alert_summary": "",
    "alert_counts": {},
    "has_critical_alerts": False,
    "alerts_done": False,
    "alert_thresholds": {},
    "final_report": "",
    "report_path": None,
    "report_done": False,
    "messages": [],
    "error": None,
    "next_agent": "news",
}

MOCK_PRICE_HISTORY: List[Dict] = [
    {"date": "2024-01-01", "open": 100.0, "high": 105.0, "low": 98.0, "close": 102.0, "volume": 1_000_000},
    {"date": "2024-01-02", "open": 102.0, "high": 110.0, "low": 101.0, "close": 108.0, "volume": 1_200_000},
    {"date": "2024-01-03", "open": 108.0, "high": 112.0, "low": 106.0, "close": 115.0, "volume": 1_100_000},
]

MOCK_STOCK_SUMMARY: Dict[str, Any] = {
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

MOCK_NEWS: List[Dict[str, Any]] = [
    {
        "title": "Apple Reports Record Earnings",
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
        "content": "The European Commission has opened a formal investigation...",
    },
]


# ---------------------------------------------------------------------------
# TestStockTools - all yfinance calls are mocked
# ---------------------------------------------------------------------------


class TestStockTools:
    def test_calculate_price_change_bullish(self):
        """Pure-Python calculation - no network needed."""
        from tools.stock_tools import calculate_price_change

        result = calculate_price_change.invoke({"price_history": MOCK_PRICE_HISTORY})
        assert "change_pct" in result
        assert result["trend"] == "Bullish"
        assert result["start_price"] == 102.0
        assert result["end_price"] == 115.0
        assert result["change_pct"] > 0

    def test_calculate_price_change_bearish(self):
        """Verify bearish detection with falling prices."""
        from tools.stock_tools import calculate_price_change

        falling = [
            {"date": "2024-01-01", "open": 115.0, "high": 116.0, "low": 110.0, "close": 112.0, "volume": 1000},
            {"date": "2024-01-02", "open": 112.0, "high": 113.0, "low": 105.0, "close": 106.0, "volume": 1200},
            {"date": "2024-01-03", "open": 106.0, "high": 107.0, "low": 98.0, "close": 100.0, "volume": 1100},
        ]
        result = calculate_price_change.invoke({"price_history": falling})
        assert result["trend"] == "Bearish"
        assert result["change_pct"] < 0

    def test_calculate_price_change_empty(self):
        """Empty input should return an error dict, not raise."""
        from tools.stock_tools import calculate_price_change

        result = calculate_price_change.invoke({"price_history": []})
        assert isinstance(result, dict)
        assert "error" in result

    @patch("tools.stock_tools.yf.Ticker")
    def test_get_stock_summary_mocked(self, mock_ticker):
        """get_stock_summary with mocked yfinance."""
        from tools.stock_tools import get_stock_summary

        mock_info = {
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
        mock_ticker.return_value.info = mock_info

        result = get_stock_summary.invoke({"ticker": "AAPL"})
        assert result["ticker"] == "AAPL"
        assert result["current_price"] == 188.52
        assert result["sector"] == "Technology"

    @patch("tools.stock_tools.yf.Ticker")
    def test_get_price_history_mocked(self, mock_ticker):
        """get_price_history with mocked yfinance response."""
        import pandas as pd

        from tools.stock_tools import get_price_history

        dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
        mock_df = pd.DataFrame(
            {
                "Open": [100.0, 102.0, 108.0],
                "High": [105.0, 110.0, 112.0],
                "Low": [98.0, 101.0, 106.0],
                "Close": [102.0, 108.0, 115.0],
                "Volume": [1_000_000, 1_200_000, 1_100_000],
            },
            index=dates,
        )
        mock_ticker.return_value.history.return_value = mock_df

        result = get_price_history.invoke({"ticker": "AAPL", "period": "5d", "interval": "1d"})
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["close"] == 102.0


# ---------------------------------------------------------------------------
# TestNewsTools - NewsAPI calls are mocked
# ---------------------------------------------------------------------------


class TestNewsTools:
    def test_fetch_financial_news_uses_mock_when_no_key(self):
        """When NEWSAPI_KEY is unset, mock data is returned automatically."""
        from tools.news_tools import fetch_financial_news

        os.environ.pop("NEWSAPI_KEY", None)
        result = fetch_financial_news.invoke({"query": "Apple", "days_back": 7})
        assert isinstance(result, list)
        assert len(result) > 0
        assert "title" in result[0]
        assert "source" in result[0]

    def test_mock_news_returns_correct_structure(self):
        """Direct mock_news helper always returns valid article structure."""
        from tools.news_tools import _mock_news

        articles = _mock_news("Tesla")
        assert len(articles) >= 3
        for article in articles:
            assert "title" in article
            assert "source" in article
            assert "publishedAt" in article
            assert "url" in article


# ---------------------------------------------------------------------------
# TestState - pure Python, no I/O
# ---------------------------------------------------------------------------


class TestState:
    def test_state_initialization(self):
        """Verify TypedDict state schema can be constructed correctly."""
        from graph.state import MarketPulseState

        state: MarketPulseState = {**MOCK_STATE}
        assert state["ticker"] == "AAPL"
        assert state["analysis_depth"] == "quick"
        assert state["news_fetched"] is False
        assert state["stock_fetched"] is False
        assert state["messages"] == []

    def test_state_message_accumulation(self):
        """Messages list should grow as agents append to it."""
        import operator

        state = {**MOCK_STATE, "messages": ["msg1"]}
        new_msgs = ["msg2", "msg3"]
        combined = operator.add(state["messages"], new_msgs)
        assert combined == ["msg1", "msg2", "msg3"]


# ---------------------------------------------------------------------------
# TestNewsAgent - mocked external call
# ---------------------------------------------------------------------------


class TestNewsAgent:
    def test_news_agent_runs_with_mock(self):
        """News agent should populate raw_news and set news_fetched=True."""
        import importlib
        import sys

        # agents/__init__.py shadows 'agents.news_agent' with the function;
        # force the real submodule into sys.modules, then grab it directly.
        importlib.import_module("agents.news_agent")
        _news_mod = sys.modules["agents.news_agent"]
        from agents.news_agent import news_agent

        with patch.object(_news_mod, "fetch_financial_news") as mock_fetch:
            mock_fetch.invoke.return_value = MOCK_NEWS
            result = news_agent({**MOCK_STATE})

        assert result["news_fetched"] is True
        assert isinstance(result["raw_news"], list)
        assert len(result["messages"]) >= 1

    def test_news_agent_empty_fallback(self):
        """When fetch returns empty, agent should still set news_fetched=True."""
        import importlib
        import sys

        importlib.import_module("agents.news_agent")
        _news_mod = sys.modules["agents.news_agent"]
        from agents.news_agent import news_agent

        with patch.object(_news_mod, "fetch_financial_news") as mock_fetch, patch.object(
            _news_mod, "fetch_top_headlines"
        ) as mock_headlines:
            mock_fetch.invoke.return_value = []
            mock_headlines.invoke.return_value = MOCK_NEWS
            result = news_agent({**MOCK_STATE})

        assert result["news_fetched"] is True


# ---------------------------------------------------------------------------
# TestStockDataAgent - mocked yfinance tools
# ---------------------------------------------------------------------------


class TestStockDataAgent:
    def test_stock_agent_populates_state(self):
        """Stock agent should fill stock_summary and set stock_fetched=True."""
        import importlib
        import sys

        # agents/__init__.py shadows 'agents.stock_data_agent' with the function;
        # use sys.modules to access the real submodule.
        importlib.import_module("agents.stock_data_agent")
        _stock_mod = sys.modules["agents.stock_data_agent"]
        from agents.stock_data_agent import stock_data_agent

        with patch.object(_stock_mod, "get_stock_summary") as mock_summary, patch.object(
            _stock_mod, "get_price_history"
        ) as mock_history, patch.object(_stock_mod, "calculate_price_change") as mock_calc:
            mock_summary.invoke.return_value = MOCK_STOCK_SUMMARY
            mock_history.invoke.return_value = MOCK_PRICE_HISTORY
            mock_calc.invoke.return_value = {
                "change_pct": 1.9,
                "trend": "Bullish",
                "start_price": 100.0,
                "end_price": 115.0,
                "highest": 115.0,
                "lowest": 98.0,
                "volatility": 6.5,
                "momentum": "Upward",
            }

            state = {**MOCK_STATE, "ticker": "MSFT", "company_name": "Microsoft Corporation"}
            result = stock_data_agent(state)

        assert result["stock_fetched"] is True
        assert isinstance(result["stock_summary"], dict)
        assert len(result["messages"]) >= 1
        mock_summary.invoke.assert_called_once()
        mock_history.invoke.assert_called_once()


# ---------------------------------------------------------------------------
# TestReportAgent - mocked LLM call
# ---------------------------------------------------------------------------


class TestReportAgent:
    def test_fallback_report_generation(self):
        """Fallback report should work without any LLM or network call."""
        from agents.report_agent import _generate_fallback_report

        state = {
            **MOCK_STATE,
            "overall_sentiment": "Bullish",
            "risk_level": "Low",
        }
        report = _generate_fallback_report(
            state,
            MOCK_STOCK_SUMMARY,
            ["Minor regulatory risk"],
            ["Strong earnings growth", "Expanding margins"],
        )
        assert "AAPL" in report
        assert "Apple Inc." in report
        assert "MarketPulse" in report
        assert "Low" in report

    def test_fallback_report_includes_risk_flags(self):
        """All risk flags should appear in the fallback report."""
        from agents.report_agent import _generate_fallback_report

        state = {**MOCK_STATE, "overall_sentiment": "Bearish", "risk_level": "High"}
        flags = ["High beta exposure", "Negative earnings trend"]
        report = _generate_fallback_report(state, MOCK_STOCK_SUMMARY, flags, [])
        for flag in flags:
            assert flag in report


# ---------------------------------------------------------------------------
# TestUtilities - pure Python, no I/O
# ---------------------------------------------------------------------------


class TestUtilities:
    def test_format_market_cap_trillions(self):
        from config.utils import format_market_cap

        assert format_market_cap(2_900_000_000_000) == "$2.90T"

    def test_format_market_cap_billions(self):
        from config.utils import format_market_cap

        assert format_market_cap(50_000_000_000) == "$50.00B"

    def test_format_market_cap_none(self):
        from config.utils import format_market_cap

        assert format_market_cap(None) == "N/A"

    def test_validate_ticker_valid(self):
        from config.utils import validate_ticker

        assert validate_ticker("AAPL") is True
        assert validate_ticker("MSFT") is True
        assert validate_ticker("BRK.B") is True

    def test_validate_ticker_invalid(self):
        from config.utils import validate_ticker

        assert validate_ticker("TOOLONGNAME") is False
        assert validate_ticker("123") is False
        assert validate_ticker("") is False

    def test_normalize_ticker(self):
        from config.utils import normalize_ticker

        assert normalize_ticker("  aapl  ") == "AAPL"
        assert normalize_ticker("tsla") == "TSLA"

    def test_format_percent_positive(self):
        from config.utils import format_percent

        assert format_percent(12.5) == "+12.50%"

    def test_format_percent_negative(self):
        from config.utils import format_percent

        assert format_percent(-3.2) == "-3.20%"

    def test_truncate(self):
        from config.utils import truncate

        # max_len=8, suffix="..." (3 chars) -> 5 chars of text + "..." = "hello..."
        assert truncate("hello world", max_len=8) == "hello..."
        # Short text should not be truncated
        assert truncate("hi", max_len=10) == "hi"
        # Exact length should not be truncated
        assert truncate("exact", max_len=5) == "exact"
