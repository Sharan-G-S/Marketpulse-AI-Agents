"""
MarketPulse — Claude & Comic UI Design System & Styling Engine
Provides unified CSS injection, Claude dark color palette, Comic pop-art palette,
and reusable UI component renderers across the application.
"""

from typing import Any, Dict, List, Optional
import plotly.graph_objects as go
import streamlit as st

CLAUDE_COLORS = {
    "bg_main": "#181816",
    "bg_card": "#22221f",
    "bg_card_hover": "#292925",
    "bg_sidebar": "#141412",
    "bg_input": "#242421",
    "border": "rgba(217, 119, 87, 0.18)",
    "border_subtle": "rgba(255, 255, 255, 0.08)",
    "terracotta": "#da7756",
    "terracotta_hover": "#c86544",
    "terracotta_light": "rgba(218, 119, 86, 0.15)",
    "gold": "#d9a74a",
    "gold_light": "rgba(217, 167, 74, 0.15)",
    "emerald": "#6fa27d",
    "emerald_light": "rgba(111, 162, 125, 0.15)",
    "rose": "#e06c68",
    "rose_light": "rgba(224, 108, 104, 0.15)",
    "blue": "#6b9ac4",
    "blue_light": "rgba(107, 154, 196, 0.15)",
    "text_primary": "#ece8e1",
    "text_secondary": "#b0aba0",
    "text_muted": "#7d786d",
}


def get_claude_css() -> str:
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Lora:ital,wght@0,500;0,600;1,400&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: {CLAUDE_COLORS["bg_main"]} !important;
        color: {CLAUDE_COLORS["text_primary"]};
    }}

    .block-container {{
        padding: 1.8rem 2.2rem !important;
        max-width: 1320px;
    }}

    h1, h2, h3, .claude-serif {{
        font-family: 'Lora', Georgia, serif !important;
        letter-spacing: -0.01em;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {CLAUDE_COLORS["bg_sidebar"]} !important;
        border-right: 1px solid {CLAUDE_COLORS["border_subtle"]} !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {CLAUDE_COLORS["terracotta"]} !important;
        font-size: 1.05rem !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {CLAUDE_COLORS["terracotta"]} 0%, #c86544 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 12px rgba(218, 119, 86, 0.25);
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, #e38363 0%, #da7756 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(218, 119, 86, 0.35);
    }}

    .stDownloadButton > button {{
        background: {CLAUDE_COLORS["bg_card"]} !important;
        color: {CLAUDE_COLORS["terracotta"]} !important;
        border: 1px solid {CLAUDE_COLORS["border"]} !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}

    .stDownloadButton > button:hover {{
        background: {CLAUDE_COLORS["terracotta_light"]} !important;
        border-color: {CLAUDE_COLORS["terracotta"]} !important;
    }}

    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div {{
        background-color: {CLAUDE_COLORS["bg_input"]} !important;
        color: {CLAUDE_COLORS["text_primary"]} !important;
        border: 1px solid {CLAUDE_COLORS["border_subtle"]} !important;
        border-radius: 8px !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: {CLAUDE_COLORS["terracotta"]} !important;
        box-shadow: 0 0 0 2px rgba(218, 119, 86, 0.2) !important;
    }}

    .claude-header {{
        background: linear-gradient(135deg, #1f1f1c 0%, #262420 100%);
        border: 1px solid {CLAUDE_COLORS["border"]};
        border-radius: 16px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }}

    .claude-header-title {{
        font-size: 2.1rem;
        font-weight: 600;
        color: {CLAUDE_COLORS["text_primary"]};
        margin: 0;
    }}

    .claude-header-sub {{
        color: {CLAUDE_COLORS["text_secondary"]};
        font-size: 0.9rem;
        margin-top: 0.35rem;
    }}

    .claude-card {{
        background-color: {CLAUDE_COLORS["bg_card"]};
        border: 1px solid {CLAUDE_COLORS["border_subtle"]};
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        transition: border-color 0.2s ease;
    }}

    .claude-card:hover {{
        border-color: {CLAUDE_COLORS["border"]};
    }}

    .claude-card-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {CLAUDE_COLORS["terracotta"]};
        margin-bottom: 0.6rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid {CLAUDE_COLORS["border_subtle"]};
    }}

    .claude-metric-card {{
        background: {CLAUDE_COLORS["bg_card"]};
        border: 1px solid {CLAUDE_COLORS["border_subtle"]};
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }}

    .claude-metric-lbl {{
        color: {CLAUDE_COLORS["text_secondary"]};
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    .claude-metric-val {{
        color: {CLAUDE_COLORS["text_primary"]};
        font-size: 1.55rem;
        font-weight: 700;
        margin: 0.25rem 0;
        font-family: 'Lora', serif;
    }}

    .claude-badge {{
        display: inline-block;
        padding: 0.3rem 0.85rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }}

    .badge-bullish {{
        background: {CLAUDE_COLORS["emerald_light"]};
        color: {CLAUDE_COLORS["emerald"]};
        border: 1px solid rgba(111, 162, 125, 0.3);
    }}

    .badge-bearish {{
        background: {CLAUDE_COLORS["rose_light"]};
        color: {CLAUDE_COLORS["rose"]};
        border: 1px solid rgba(224, 108, 104, 0.3);
    }}

    .badge-neutral {{
        background: {CLAUDE_COLORS["gold_light"]};
        color: {CLAUDE_COLORS["gold"]};
        border: 1px solid rgba(217, 167, 74, 0.3);
    }}

    .badge-terracotta {{
        background: {CLAUDE_COLORS["terracotta_light"]};
        color: {CLAUDE_COLORS["terracotta"]};
        border: 1px solid {CLAUDE_COLORS["border"]};
    }}

    .claude-flag-risk {{
        background: {CLAUDE_COLORS["rose_light"]};
        border-left: 3px solid {CLAUDE_COLORS["rose"]};
        padding: 0.6rem 0.95rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        color: #f7aaaa;
        font-size: 0.84rem;
    }}

    .claude-flag-insight {{
        background: {CLAUDE_COLORS["emerald_light"]};
        border-left: 3px solid {CLAUDE_COLORS["emerald"]};
        padding: 0.6rem 0.95rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        color: #b7e3c4;
        font-size: 0.84rem;
    }}

    .claude-news-item {{
        background: {CLAUDE_COLORS["bg_card"]};
        border: 1px solid {CLAUDE_COLORS["border_subtle"]};
        border-radius: 10px;
        padding: 0.95rem;
        margin-bottom: 0.65rem;
    }}

    .claude-news-item:hover {{
        border-color: {CLAUDE_COLORS["border"]};
    }}

    div[data-testid="stDataFrame"] {{
        background-color: {CLAUDE_COLORS["bg_card"]};
        border-radius: 10px;
    }}

    .stExpander {{
        background-color: {CLAUDE_COLORS["bg_card"]} !important;
        border: 1px solid {CLAUDE_COLORS["border_subtle"]} !important;
        border-radius: 10px !important;
    }}
    </style>
    """


def apply_claude_theme():
    st.markdown(get_claude_css(), unsafe_allow_html=True)


def apply_theme_by_name(theme_name: str = "claude"):
    """Applies theme dynamically by name ('claude' or 'comic')."""
    if theme_name.lower() == "comic":
        from ui.comic_theme import apply_comic_theme
        apply_comic_theme()
    else:
        apply_claude_theme()


def get_claude_plotly_layout(height: int = 340, title: str = "") -> Dict[str, Any]:
    return dict(
        title=dict(text=title, font=dict(family="Lora, serif", size=15, color=CLAUDE_COLORS["text_primary"])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(34,34,31,0.5)",
        font=dict(family="Inter, sans-serif", color=CLAUDE_COLORS["text_secondary"], size=11),
        margin=dict(l=15, r=15, t=35 if title else 15, b=15),
        height=height,
        showlegend=True,
        legend=dict(
            font=dict(color=CLAUDE_COLORS["text_secondary"]),
            bgcolor="rgba(20,20,18,0.8)",
            bordercolor="rgba(255,255,255,0.08)",
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(color=CLAUDE_COLORS["text_secondary"]),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(color=CLAUDE_COLORS["text_secondary"]),
        ),
    )


def render_claude_header(title: str, subtitle: str, icon: str = "🧡"):
    st.markdown(
        f"""
        <div class="claude-header">
            <div class="claude-header-title">{icon} {title}</div>
            <div class="claude-header-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
