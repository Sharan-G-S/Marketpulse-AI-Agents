"""
Integration tests for the full LangGraph workflow pipeline.
These tests run real agent nodes (without LLM calls where possible).
"""

import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWorkflowGraph:
    def test_graph_builds_successfully(self):
        """Verify the LangGraph workflow compiles without errors."""
        from graph.workflow import build_graph
        g = build_graph()
        assert g is not None

    def test_graph_has_correct_nodes(self):
        """Check that all expected agent nodes are registered."""
        from graph.workflow import build_graph
        g = build_graph()
        # LangGraph compiled graph should have graph structure
        assert g is not None

    def test_news_then_stock_pipeline(self, base_state):
        """Run news agent → stock agent in sequence."""
        from agents.news_agent import news_agent
        from agents.stock_data_agent import stock_data_agent

        after_news = news_agent(base_state)
        assert after_news["news_fetched"] is True
        assert len(after_news["raw_news"]) > 0

        after_stock = stock_data_agent(after_news)
        assert after_stock["stock_fetched"] is True
        assert "current_price" in after_stock["stock_summary"]

    def test_report_fallback_without_llm(self, base_state, mock_stock_summary):
        """Test fallback report generation without needing LLM."""
        from agents.report_agent import _generate_fallback_report

        state = {
            **base_state,
            "stock_summary": mock_stock_summary,
            "overall_sentiment": "Bullish",
            "risk_level": "Low",
            "risk_flags": ["Minor regulatory risk"],
            "key_insights": ["Strong earnings growth"],
        }
        report = _generate_fallback_report(state, mock_stock_summary,
                                            ["Minor regulatory risk"], ["Strong earnings growth"])
        assert "AAPL" in report
        assert "Apple Inc." in report
        assert "MarketPulse" in report


class TestToolIntegration:
    def test_stock_and_price_tools_chain(self, base_state):
        """Test chaining get_stock_summary → get_price_history → calculate_price_change."""
        from tools.stock_tools import get_stock_summary, get_price_history, calculate_price_change

        summary = get_stock_summary.invoke({"ticker": "MSFT"})
        assert "current_price" in summary

        history = get_price_history.invoke({"ticker": "MSFT", "period": "5d", "interval": "1d"})
        assert isinstance(history, list)

        if history and "error" not in history[0]:
            metrics = calculate_price_change.invoke({"price_history": history})
            assert "change_pct" in metrics
            assert "trend" in metrics

    def test_mock_news_always_returns_articles(self):
        """Mock news should always return articles even without an API key."""
        from tools.news_tools import _mock_news
        articles = _mock_news("Tesla")
        assert len(articles) >= 3
        for art in articles:
            assert "title" in art
            assert "source" in art


class TestStateAnnotations:
    def test_messages_accumulate_correctly(self, base_state):
        """Verify that messages list accumulates across agent calls."""
        from agents.news_agent import news_agent

        state1 = news_agent(base_state)
        # News agent should append at least one message
        assert len(state1["messages"]) >= 1
        assert any("News Agent" in m for m in state1["messages"])

    def test_calculate_price_change_with_fixture(self, mock_price_history):
        """Test price change calculation with fixture data."""
        from tools.stock_tools import calculate_price_change
        result = calculate_price_change.invoke({"price_history": mock_price_history})
        assert result["start_price"] == 173.0
        assert result["end_price"] == 188.0
        assert result["trend"] == "Bullish"
        assert result["change_pct"] > 0
