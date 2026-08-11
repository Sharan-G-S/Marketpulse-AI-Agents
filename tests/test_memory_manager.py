"""
Unit tests for memory/memory_manager.py
"""

from memory.memory_manager import summarize_state_snapshot, trim_message_history


def test_trim_message_history():
    msgs = [f"Message {i}" for i in range(25)]
    trimmed = trim_message_history(msgs, max_messages=5)
    assert len(trimmed) == 5
    assert trimmed[-1] == "Message 24"


def test_summarize_state_snapshot():
    state = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "overall_sentiment": "Bullish",
        "risk_level": "Low",
        "raw_news": [{}, {}, {}],
        "final_report": "Sample Report",
    }
    summary = summarize_state_snapshot(state)
    assert summary["ticker"] == "AAPL"
    assert summary["article_count"] == 3
    assert summary["has_report"] is True
