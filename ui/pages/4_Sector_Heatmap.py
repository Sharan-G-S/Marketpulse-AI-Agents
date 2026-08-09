"""
Sector Heatmap — Streamlit Page for MarketPulse.
Displays live sector performance heatmap in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS, get_claude_plotly_layout
from agents.watchlist_agent import WATCHLIST_DEFAULTS
from tools.heatmap_helpers import format_heatmap_summary, format_heatmap_table, heatmap_to_dicts
from tools.sector_heatmap import build_sector_heatmap

st.set_page_config(page_title="Sector Heatmap — MarketPulse", page_icon="🌡️", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Sector Performance Heatmap",
    subtitle="Scan market sectors, compute heatmap scores, and detect capital flow momentum",
    icon="🌡️"
)

st.sidebar.markdown("### ⚙️ Heatmap Controls")
use_custom = st.sidebar.checkbox("Custom Ticker List", value=False)
if use_custom:
    user_input = st.sidebar.text_area("Enter Tickers (comma separated)", value="AAPL, MSFT, NVDA, GOOGL, AMZN, JPM, XOM, TSLA")
    tickers = [t.strip().upper() for t in user_input.split(",") if t.strip()]
else:
    tickers = WATCHLIST_DEFAULTS

run_scan = st.sidebar.button("🌡️ Refresh Sector Heatmap", use_container_width=True)

if "heatmap_data" not in st.session_state or run_scan:
    with st.spinner("Scanning sector price performance & volume momentum..."):
        try:
            st.session_state.heatmap_data = build_sector_heatmap(tickers)
        except Exception as e:
            st.error(f"Failed to scan sector heatmap: {e}")
            st.session_state.heatmap_data = {}

heatmap = st.session_state.get("heatmap_data", {})

if heatmap:
    # Render Bar Chart of Sector Change
    sectors = list(heatmap.keys())
    changes = [heatmap[s].get("avg_change_pct", 0) for s in sectors]
    colors = [CLAUDE_COLORS["emerald"] if c >= 0 else CLAUDE_COLORS["rose"] for c in changes]

    fig = go.Figure(go.Bar(
        x=sectors,
        y=changes,
        marker_color=colors,
        text=[f"{c:+.2f}%" for c in changes],
        textposition="outside",
        textfont=dict(color=CLAUDE_COLORS["text_primary"]),
    ))
    fig.update_layout(get_claude_plotly_layout(height=350, title="Average Sector Daily Change (%)"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='claude-card-title'>📊 Sector Performance Breakdown</div>", unsafe_allow_html=True)
    dict_rows = heatmap_to_dicts(heatmap)
    if dict_rows:
        df = pd.DataFrame(dict_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Click 'Refresh Sector Heatmap' in the sidebar to scan sector momentum.")
