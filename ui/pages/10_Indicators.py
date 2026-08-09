"""
Technical Indicator Dashboard — Streamlit Page for MarketPulse.
RSI, MACD, Moving Average crossover, & Bollinger Band signals in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS
from tools.stock_tools import get_price_history
from tools.indicators import get_all_indicators

st.set_page_config(page_title="Indicators — MarketPulse", page_icon="📉", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Technical Indicator Suite",
    subtitle="RSI, MACD, Bollinger Bands, Moving Average crossovers, Stochastic Oscillators & ATR",
    icon="📉"
)

st.sidebar.markdown("### ⚙️ Technical Settings")
ticker = st.sidebar.text_input("Stock Ticker Symbol", value="AAPL").strip().upper()
period = st.sidebar.selectbox("History Horizon", ["1mo", "3mo", "6mo", "1y"], index=1)
calc_btn = st.sidebar.button("📉 Calculate Indicators", use_container_width=True)

if calc_btn or "ind_results" in st.session_state:
    if calc_btn:
        with st.spinner(f"Computing technical indicators for {ticker}..."):
            try:
                df = get_price_history.invoke({"ticker": ticker, "period": period, "interval": "1d"})
                inds = get_all_indicators(df)
                st.session_state.ind_results = inds
            except Exception as e:
                st.error(f"Indicator calculation failed: {e}")
                st.session_state.ind_results = {}

    inds = st.session_state.get("ind_results", {})
    if inds:
        st.markdown("<div class='claude-card-title'>📊 Computed Technical Metrics</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        cols[0].metric("RSI (14)", f"{inds.get('rsi', 0):.2f}" if inds.get('rsi') else "N/A")
        cols[1].metric("MACD", f"{inds.get('macd', 0):.2f}" if inds.get('macd') else "N/A")
        cols[2].metric("SMA 20", f"${inds.get('sma_20', 0):.2f}" if inds.get('sma_20') else "N/A")
        cols[3].metric("SMA 50", f"${inds.get('sma_50', 0):.2f}" if inds.get('sma_50') else "N/A")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='claude-card-title'>📋 Full Indicators Summary Table</div>", unsafe_allow_html=True)
        df_inds = pd.DataFrame([{"Indicator": k, "Value": str(v)} for k, v in inds.items()])
        st.dataframe(df_inds, use_container_width=True, hide_index=True)
else:
    st.info("Enter a ticker symbol and click 'Calculate Indicators' in the sidebar.")
