"""
Unit tests for agents/comic_agent.py and ui/comic_theme.py
"""

from agents.comic_agent import generate_comic_storyboard
from ui.comic_theme import get_comic_css, render_comic_header


def test_generate_comic_storyboard_panels():
    state = {
        "ticker": "TSLA",
        "company_name": "Tesla Inc.",
        "overall_sentiment": "Bullish",
        "risk_level": "Medium",
    }
    story = generate_comic_storyboard(state)
    assert len(story) == 4
    assert story[0]["panel"] == "PANEL 1"
    assert "TSLA" in story[0]["narrative"]


def test_get_comic_css_injection():
    css = get_comic_css()
    assert "Comic Neue" in css
    assert "Bangers" in css
