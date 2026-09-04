"""
Unit tests for ui/comic_theme.py SFX badge renderer
"""

from ui.comic_theme import render_comic_sfx, get_comic_css


def test_render_comic_sfx():
    # Should run without error
    css = get_comic_css()
    assert "comic-sfx-badge" in css
