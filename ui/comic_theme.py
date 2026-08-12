"""
MarketPulse — Comic & Graphic Novel Financial UI Theme Engine
Provides vibrant pop-art styling, speech bubble cards, comic badges,
and custom Plotly pop-art chart layouts.
"""

from typing import Any, Dict
import plotly.graph_objects as go
import streamlit as st

COMIC_COLORS = {
    "yellow": "#ffde59",
    "red": "#ff3131",
    "cyan": "#00f0ff",
    "green": "#00e676",
    "purple": "#9c27b0",
    "bubble_bg": "#fffdf0",
    "card_bg": "#ffffff",
    "ink_black": "#121212",
    "border": "#000000",
    "text_dark": "#121212",
    "text_muted": "#555555",
}


def get_comic_css() -> str:
    """Returns full Comic / Pop-Art CSS ruleset for Streamlit injection."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&display=swap');

    /* Base Reset & Comic Typography */
    html, body, [class*="css"], .stApp {{
        font-family: 'Comic Neue', 'Chalkboard', cursive, sans-serif !important;
        background-color: #f8f6ee !important;
        color: {COMIC_COLORS["ink_black"]};
    }}

    .block-container {{
        padding: 1.5rem 2rem !important;
        max-width: 1300px;
    }}

    h1, h2, h3, .comic-title {{
        font-family: 'Bangers', cursive, impact !important;
        letter-spacing: 0.05em;
        color: {COMIC_COLORS["ink_black"]};
        text-transform: uppercase;
        text-shadow: 2px 2px 0px {COMIC_COLORS["yellow"]};
    }}

    /* Sidebar Comic Styling */
    section[data-testid="stSidebar"] {{
        background-color: {COMIC_COLORS["yellow"]} !important;
        border-right: 4px solid {COMIC_COLORS["ink_black"]} !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {COMIC_COLORS["red"]} !important;
        text-shadow: 2px 2px 0px #000000 !important;
    }}

    /* Comic Action Buttons */
    .stButton > button {{
        background: {COMIC_COLORS["red"]} !important;
        color: #ffffff !important;
        border: 3px solid {COMIC_COLORS["border"]} !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.6rem !important;
        font-family: 'Bangers', cursive !important;
        font-size: 1.25rem !important;
        letter-spacing: 0.06em !important;
        box-shadow: 5px 5px 0px {COMIC_COLORS["ink_black"]} !important;
        transition: all 0.15s ease !important;
    }}

    .stButton > button:hover {{
        background: {COMIC_COLORS["yellow"]} !important;
        color: {COMIC_COLORS["ink_black"]} !important;
        transform: translate(-2px, -2px);
        box-shadow: 7px 7px 0px {COMIC_COLORS["ink_black"]} !important;
    }}

    /* Input Controls */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {{
        background-color: #ffffff !important;
        color: {COMIC_COLORS["ink_black"]} !important;
        border: 3px solid {COMIC_COLORS["border"]} !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 3px 3px 0px {COMIC_COLORS["ink_black"]} !important;
    }}

    /* Speech Bubble Cards */
    .comic-bubble {{
        position: relative;
        background: {COMIC_COLORS["bubble_bg"]};
        border: 4px solid {COMIC_COLORS["border"]};
        border-radius: 20px;
        padding: 1.3rem 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 6px 6px 0px {COMIC_COLORS["ink_black"]};
    }}

    .comic-card-title {{
        font-family: 'Bangers', cursive !important;
        font-size: 1.4rem;
        color: {COMIC_COLORS["red"]};
        margin-bottom: 0.5rem;
    }}

    .comic-starburst {{
        display: inline-block;
        background: {COMIC_COLORS["yellow"]};
        color: {COMIC_COLORS["ink_black"]};
        border: 3px solid {COMIC_COLORS["border"]};
        padding: 0.35rem 1rem;
        font-family: 'Bangers', cursive;
        font-size: 1.1rem;
        transform: rotate(-3deg);
        box-shadow: 3px 3px 0px {COMIC_COLORS["border"]};
    }}
    </style>
    """


def apply_comic_theme():
    """Injects Comic design system into Streamlit page."""
    st.markdown(get_comic_css(), unsafe_allow_html=True)


def get_comic_plotly_layout(height: int = 340, title: str = "") -> Dict[str, Any]:
    """Returns Plotly pop-art layout matching comic aesthetic."""
    return dict(
        title=dict(text=title, font=dict(family="Bangers, cursive", size=18, color=COMIC_COLORS["ink_black"])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Comic Neue, sans-serif", color=COMIC_COLORS["ink_black"], size=12),
        margin=dict(l=20, r=20, t=40 if title else 20, b=20),
        height=height,
        showlegend=True,
        xaxis=dict(
            gridcolor="#e0e0e0",
            linecolor=COMIC_COLORS["border"],
            linewidth=3,
        ),
        yaxis=dict(
            gridcolor="#e0e0e0",
            linecolor=COMIC_COLORS["border"],
            linewidth=3,
        ),
    )


def render_comic_header(title: str, subtitle: str, icon: str = "💥"):
    """Renders pop-art comic header section."""
    st.markdown(
        f"""
        <div class="comic-bubble" style="background:{COMIC_COLORS['yellow']};">
            <div style="font-family:'Bangers',cursive;font-size:2.4rem;color:{COMIC_COLORS['red']};text-shadow:3px 3px 0px #000;">
                {icon} {title}
            </div>
            <div style="font-weight:700;font-size:1.05rem;color:{COMIC_COLORS['ink_black']};margin-top:0.3rem;">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
