"""
Unit tests for ui/comic_theme.py and agents/comic_agent.py
"""

from agents.comic_agent import generate_comic_storyboard
from ui.comic_theme import COMIC_COLORS, get_comic_css, get_comic_plotly_layout


def test_comic_colors_contain_tokens():
    assert "yellow" in COMIC_COLORS
    assert COMIC_COLORS["yellow"] == "#ffde59"
    assert COMIC_COLORS["red"] == "#ff3131"


def test_get_comic_css():
    css = get_comic_css()
    assert "Comic Neue" in css
    assert "comic-bubble" in css


def test_generate_comic_storyboard():
    state = {"ticker": "AAPL", "company_name": "Apple Inc.", "overall_sentiment": "Bullish", "risk_level": "Low"}
    story = generate_comic_storyboard(state)
    assert len(story) == 4
    assert story[0]["panel"] == "PANEL 1"
    assert "AAPL" in story[0]["narrative"]
