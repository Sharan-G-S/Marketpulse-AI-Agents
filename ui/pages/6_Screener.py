"""
Gainers & Losers Screener — Streamlit Page for MarketPulse.
Scans stock universe, ranks daily gainers & losers, and visualizes market breadth in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS, get_claude_plotly_layout
from agents.screener_agent import SCREENER_UNIVERSE, run_screener, screener_breadth
from tools.screener_helpers import format_screener_table, screener_entries_to_dicts

st.set_page_config(page_title="Screener — MarketPulse", page_icon="🔍", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Market Movers & Stock Screener",
    subtitle="Scan gainers, losers, volume spikes, and advance/decline breadth across market universe",
    icon="🔍"
)

st.sidebar.markdown("### ⚙️ Screener Controls")
top_n = st.sidebar.slider("Top Gainers / Losers Count", min_value=3, max_value=15, value=5)
run_scr = st.sidebar.button("🔍 Run Market Screener", use_container_width=True)

if "screener_data" not in st.session_state or run_scr:
    with st.spinner("Scanning market universe for top gainers & volume spikes..."):
        try:
            st.session_state.screener_data = run_screener(top_n=top_n)
        except Exception as e:
            st.error(f"Screener failed: {e}")
            st.session_state.screener_data = {}

scr_data = st.session_state.get("screener_data", {})

if scr_data:
    gainers = scr_data.get("gainers", [])
    losers = scr_data.get("losers", [])
    most_active = scr_data.get("most_active", [])
    adv = scr_data.get("advances", 0)
    dec = scr_data.get("declines", 0)

    # Breadth Donut Chart
    cols = st.columns([1, 2])
    with cols[0]:
        st.markdown("<div class='claude-card-title'>📊 Market Advance / Decline</div>", unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=["Advances", "Declines"],
            values=[adv, dec],
            hole=0.6,
            marker=dict(colors=[CLAUDE_COLORS["emerald"], CLAUDE_COLORS["rose"]]),
            textinfo="label+value",
            textfont=dict(color=CLAUDE_COLORS["text_primary"]),
        ))
        fig.update_layout(get_claude_plotly_layout(height=260))
        st.plotly_chart(fig, use_container_width=True)

    with cols[1]:
        st.markdown("<div class='claude-card-title'>🚀 Top Market Gainers</div>", unsafe_allow_html=True)
        if gainers:
            df_g = pd.DataFrame(screener_entries_to_dicts(gainers))
            st.dataframe(df_g, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='claude-card-title'>📉 Top Market Decliners</div>", unsafe_allow_html=True)
    if losers:
        df_l = pd.DataFrame(screener_entries_to_dicts(losers))
        st.dataframe(df_l, use_container_width=True, hide_index=True)
else:
    st.info("Click 'Run Market Screener' in the sidebar to scan for top movers.")
