"""
Sentiment Trend — Streamlit Page for MarketPulse.
Visualizes news sentiment scores over time in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS, get_claude_plotly_layout
from tools.sentiment_trend import build_sentiment_trend, sentiment_label, trend_direction

st.set_page_config(page_title="Sentiment Trend — MarketPulse", page_icon="🧠", layout="wide")
apply_claude_theme()

render_claude_header(
    title="News Sentiment Trend Analytics",
    subtitle="Track historical sentiment trajectories, news velocity, and bullish vs bearish sentiment shifts",
    icon="🧠"
)

st.sidebar.markdown("### ⚙️ Trend Controls")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").strip().upper()
days = st.sidebar.slider("Historical Days Back", min_value=3, max_value=30, value=7)
gen_btn = st.sidebar.button("🧠 Build Sentiment Trend", use_container_width=True)

if gen_btn or "sentiment_trend_df" in st.session_state:
    if gen_btn:
        with st.spinner(f"Computing sentiment trajectory for {ticker}..."):
            try:
                st.session_state.sentiment_trend_df = build_sentiment_trend(ticker, days=days)
            except Exception as e:
                st.error(f"Sentiment trend generation failed: {e}")
                st.session_state.sentiment_trend_df = pd.DataFrame()

    df_trend = st.session_state.get("sentiment_trend_df")

    if df_trend is not None and not df_trend.empty:
        st.markdown("<div class='claude-card-title'>📈 Sentiment Trajectory (-1.0 Bearish to +1.0 Bullish)</div>", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_trend["date"],
            y=df_trend["avg_score"],
            mode="lines+markers",
            line=dict(color=CLAUDE_COLORS["terracotta"], width=3),
            marker=dict(size=8, color=CLAUDE_COLORS["terracotta"]),
            name="Sentiment Score",
        ))
        layout = get_claude_plotly_layout(height=350)
        layout["yaxis"]["range"] = [-1.1, 1.1]
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='claude-card-title'>📋 Daily Sentiment Breakdown</div>", unsafe_allow_html=True)
        st.dataframe(df_trend, use_container_width=True, hide_index=True)
else:
    st.info("Enter a ticker symbol and click 'Build Sentiment Trend' to analyze sentiment history.")
