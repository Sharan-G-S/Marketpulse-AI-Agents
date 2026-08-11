"""
MarketPulse — Streamlit State Manager & Persistence Helper
Manages atomic session state re-hydration across Streamlit page navigation.
"""

from typing import Any, Dict
import streamlit as st


def get_state_var(key: str, default: Any = None) -> Any:
    """Retrieves session state variable safely."""
    if not hasattr(st, "session_state"):
        return default
    return st.session_state.get(key, default)


def set_state_var(key: str, value: Any):
    """Sets session state variable safely."""
    if hasattr(st, "session_state"):
        st.session_state[key] = value


def persist_analysis_result(result_data: Dict[str, Any]):
    """Persists analysis result snapshot across session tabs."""
    if hasattr(st, "session_state") and isinstance(result_data, dict):
        st.session_state["result"] = result_data
        st.session_state["last_ticker"] = result_data.get("ticker", "")
