"""
MarketPulse — Institutional Order Flow & Dark Pool Tracker Page
Scans off-exchange volume ratios, block trade spikes, and institutional accumulation anomalies.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import CLAUDE_COLORS, apply_theme_by_name, render_claude_header, get_claude_plotly_layout
from tools.dark_pool_tracker import detect_dark_pool_activity

st.set_page_config(page_title="Institutional Order Flow — MarketPulse", page_icon="🏦", layout="wide")
apply_theme_by_name("claude")

render_claude_header(
    title="Institutional Order Flow & Dark Pool Tracker",
    subtitle="Off-Exchange Volume Anomaly Scanner & Block Trade Accumulation Detector",
    icon="🏦"
)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='claude-card-title'>⚙️ Volume Input Parameters</div>", unsafe_allow_html=True)
    cur_vol = st.number_input("Current Daily Volume", value=15000000, step=1000000)
    avg_vol = st.number_input("30-Day Avg Volume", value=5000000, step=1000000)

    res = detect_dark_pool_activity(cur_vol, avg_vol)

    ratio = res.get("volume_ratio", 1.0)
    signal = res.get("signal", "Normal")
    is_ano = res.get("is_anomaly", False)

    badge_cls = "badge-bearish" if is_ano and ratio > 2.0 else "badge-neutral"

    st.markdown(
        f"""
        <div class="claude-card" style="margin-top:1rem;">
            <div style="color:{CLAUDE_COLORS['text_secondary']};font-size:0.8rem;">VOLUME RATIO</div>
            <div style="font-size:2.2rem;font-weight:700;color:{CLAUDE_COLORS['terracotta']};">{ratio:.2f}x</div>
            <div style="margin-top:0.5rem;">
                <span class="claude-badge {badge_cls}">⚠️ {signal}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown("<div class='claude-card-title'>📊 Simulated Institutional Volume Distribution</div>", unsafe_allow_html=True)
    df = pd.DataFrame({
        "Venue": ["Lit Exchange (NYSE/Nasdaq)", "Dark Pool Off-Exchange", "OTC Internalized"],
        "Volume": [cur_vol * 0.45, cur_vol * 0.35, cur_vol * 0.20],
    })
    fig = go.Figure(go.Pie(
        labels=df["Venue"],
        values=df["Volume"],
        hole=0.55,
        marker=dict(colors=[CLAUDE_COLORS["blue"], CLAUDE_COLORS["terracotta"], CLAUDE_COLORS["gold"]]),
    ))
    fig.update_layout(get_claude_plotly_layout(height=320, title="Order Execution Venue Breakdown"))
    st.plotly_chart(fig, use_container_width=True)
