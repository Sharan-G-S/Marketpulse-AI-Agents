"""
MarketPulse — Agent Memory Manager & Conversation Trimmer
Manages memory history trimming and state snapshot persistence to optimize token windows.
"""

from typing import Any, Dict, List


def trim_message_history(messages: List[str], max_messages: int = 10) -> List[str]:
    """
    Trims agent execution log message history to the most recent max_messages items.
    """
    if not isinstance(messages, list):
        return []
    if len(messages) <= max_messages:
        return messages
    return messages[-max_messages:]


def summarize_state_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a compact summary representation of a MarketPulseState snapshot.
    """
    if not isinstance(state, dict):
        return {}

    return {
        "ticker": state.get("ticker", ""),
        "company_name": state.get("company_name", ""),
        "overall_sentiment": state.get("overall_sentiment", "Neutral"),
        "risk_level": state.get("risk_level", "Medium"),
        "article_count": len(state.get("raw_news", [])),
        "has_report": bool(state.get("final_report")),
    }
