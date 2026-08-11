"""
Unit tests for ui/state_manager.py
"""

from ui.state_manager import get_state_var, set_state_var


def test_get_set_state_var():
    set_state_var("test_key", "test_val")
    val = get_state_var("test_key")
    assert val == "test_val"
