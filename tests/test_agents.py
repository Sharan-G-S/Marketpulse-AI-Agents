"""
MarketPulse — Basic Unit Tests
Run with: pytest tests/ -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Tool Tests ─────────────────────────────────────────────────────────────────
class TestStockTools:
    def test_get_stock_summary_valid(self):
        from tools.stock_tools import get_stock_summary
        result = get_stock_summary.invoke({"ticker": "AAPL"})
        assert "ticker" in result
        assert result["ticker"] == "AAPL"
        assert "current_price" in result

    def test_get_stock_summary_invalid(self):
        from tools.stock_tools import get_stock_summary
        result = get_stock_summary.invoke({"ticker": "INVALIDXYZ999"})
        # Should return some result without crashing
        assert isinstance(result, dict)

    def test_get_price_history(self):
        from tools.stock_tools import get_price_history
        result = get_price_history.invoke({"ticker": "AAPL", "period": "5d", "interval": "1d"})
        assert isinstance(result, list)

    def test_calculate_price_change(self):
        from tools.stock_tools import calculate_price_change
        mock_history = [
            {"date": "2024-01-01", "open": 100, "high": 105, "low": 98, "close": 102, "volume": 1000},
            {"date": "2024-01-02", "open": 102, "high": 110, "low": 101, "close": 108, "volume": 1200},
            {"date": "2024-01-03", "open": 108, "high": 112, "low": 106, "close": 115, "volume": 1100},
        ]
        result = calculate_price_change.invoke({"price_history": mock_history})
        assert "change_pct" in result
        assert result["trend"] == "Bullish"
        assert result["start_price"] == 102


class TestNewsTools:
    def test_fetch_financial_news_mock(self):
        """Test that mock news is returned when no API key is set."""
        from tools.news_tools import fetch_financial_news
        os.environ.pop("NEWSAPI_KEY", None)
        result = fetch_financial_news.invoke({"query": "Apple", "days_back": 7})
        assert isinstance(result, list)
        assert len(result) > 0
        assert "title" in result[0]


# ── State Tests ────────────────────────────────────────────────────────────────
class TestState:
    def test_state_initialization(self):
        from graph.state import MarketPulseState
        state: MarketPulseState = {
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "analysis_depth": "standard",
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
        assert state["ticker"] == "AAPL"
        assert state["analysis_depth"] == "standard"


# ── Agent Unit Tests (no LLM calls) ──────────────────────────────────────────
class TestNewsAgent:
    def test_news_agent_runs(self):
        from agents.news_agent import news_agent
        state = {
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "analysis_depth": "quick",
            "raw_news": [], "news_fetched": False,
            "sentiment_scores": [], "overall_sentiment": "Neutral",
            "sentiment_confidence": 0.0, "sentiment_done": False,
            "stock_summary": {}, "price_history": [], "stock_fetched": False,
            "risk_flags": [], "risk_level": "Medium",
            "key_insights": [], "risk_done": False,
            "final_report": "", "report_path": None, "report_done": False,
            "messages": [], "error": None, "next_agent": "news",
        }
        result = news_agent(state)
        assert result["news_fetched"] is True
        assert isinstance(result["raw_news"], list)


class TestStockDataAgent:
    def test_stock_data_agent_runs(self):
        from agents.stock_data_agent import stock_data_agent
        state = {
            "ticker": "MSFT",
            "company_name": "Microsoft Corporation",
            "analysis_depth": "quick",
            "raw_news": [], "news_fetched": False,
            "sentiment_scores": [], "overall_sentiment": "Neutral",
            "sentiment_confidence": 0.0, "sentiment_done": False,
            "stock_summary": {}, "price_history": [], "stock_fetched": False,
            "risk_flags": [], "risk_level": "Medium",
            "key_insights": [], "risk_done": False,
            "final_report": "", "report_path": None, "report_done": False,
            "messages": [], "error": None, "next_agent": "stock",
        }
        result = stock_data_agent(state)
        assert result["stock_fetched"] is True
        assert "current_price" in result["stock_summary"]
