"""
Unit tests for Claude UI theme engine (ui/theme.py).
"""

from ui.theme import CLAUDE_COLORS, apply_claude_theme, get_claude_css, get_claude_plotly_layout


def test_claude_colors_contain_tokens():
    assert "bg_main" in CLAUDE_COLORS
    assert "terracotta" in CLAUDE_COLORS
    assert CLAUDE_COLORS["terracotta"] == "#da7756"
    assert CLAUDE_COLORS["bg_main"] == "#181816"


def test_get_claude_css_returns_stylesheet():
    css = get_claude_css()
    assert "<style>" in css
    assert "#da7756" in css
    assert "#181816" in css
    assert "claude-header" in css


def test_get_claude_plotly_layout():
    layout = get_claude_plotly_layout(height=400, title="Test Chart")
    assert layout["height"] == 400
    assert layout["paper_bgcolor"] == "rgba(0,0,0,0)"
    assert layout["title"]["text"] == "Test Chart"
