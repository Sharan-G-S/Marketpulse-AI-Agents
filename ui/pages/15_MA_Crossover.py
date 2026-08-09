"""
MA Crossover Signals — Streamlit page for MarketPulse.
Golden Cross & Death Cross technical crossover analysis in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS
from tools.ma_crossover import ma_crossover_summary

st.set_page_config(page_title="MA Crossover — MarketPulse", page_icon="📉", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Moving Average Crossover Intelligence",
    subtitle="Detect Golden Cross & Death Cross trend reversals using SMA / EMA technical indicators",
    icon="📉"
)

st.sidebar.markdown("### ⚙️ MA Crossover Settings")
raw = st.sidebar.text_input("Tickers (comma-separated)", value="AAPL, MSFT, TSLA", key="ma_tickers")
fast = st.sidebar.number_input("Fast MA Period", min_value=5, max_value=100, value=50, step=5)
slow = st.sidebar.number_input("Slow MA Period", min_value=20, max_value=400, value=200, step=10)
use_ema = st.sidebar.checkbox("Exponential MA (EMA)", value=False)
run_btn = st.sidebar.button("📉 Compute MA Crossovers", use_container_width=True)

tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

if run_btn or "ma_summaries" in st.session_state:
    if run_btn and tickers:
        with st.spinner("Fetching historical OHLC & computing MA crossovers..."):
            try:
                from tools.stock_tools import get_price_history
                summaries = {}
                for t in tickers:
                    try:
                        hist = get_price_history.invoke({"ticker": t, "period": "1y", "interval": "1d"})
                        summaries[t] = ma_crossover_summary(hist, fast_period=fast, slow_period=slow, use_ema=use_ema)
                    except Exception:
                        pass
                st.session_state["ma_summaries"] = summaries
            except Exception as e:
                st.error(f"MA Crossover calculation failed: {e}")

    summaries = st.session_state.get("ma_summaries", {})
    if summaries:
        st.markdown("<div class='claude-card-title'>📋 MA Crossover Signals Summary</div>", unsafe_allow_html=True)
        rows = []
        for t, s in summaries.items():
            rows.append({
                "Ticker": t,
                "Signal": s.get("current_signal", "—"),
                "Fast MA": s.get("fast_value"),
                "Slow MA": s.get("slow_value"),
                "N Crossovers": len(s.get("crossover_events", [])),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("Enter tickers in the sidebar and click 'Compute MA Crossovers' to start.")
