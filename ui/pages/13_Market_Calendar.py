"""
Market Calendar Page — Streamlit UI for MarketPulse.
Upcoming earnings, ex-dividend dates, & US market holidays in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS
from tools.market_calendar import build_market_calendar, upcoming_earnings_list

st.set_page_config(page_title="Market Calendar — MarketPulse", page_icon="📅", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Financial Market Calendar & Catalyst Watch",
    subtitle="Monitor upcoming earnings release dates, ex-dividend events, and market holidays",
    icon="📅"
)

st.sidebar.markdown("### ⚙️ Calendar Settings")
raw = st.sidebar.text_input("Tickers (comma-separated)", value="AAPL, MSFT, TSLA, NVDA", key="cal_tickers")
days_ahead = st.sidebar.slider("Scan Days Ahead", 7, 90, 30)
run_btn = st.sidebar.button("📅 Load Market Calendar", use_container_width=True)

tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

if run_btn or "cal_events" in st.session_state:
    if run_btn and tickers:
        with st.spinner("Fetching ticker earnings & dividend schedules..."):
            try:
                from tools.stock_tools import get_stock_summary
                summaries = {t: get_stock_summary.invoke({"ticker": t}) for t in tickers if t}
                events = build_market_calendar(summaries, days_ahead=days_ahead)
                st.session_state.cal_events = events
            except Exception as e:
                st.error(f"Calendar scan failed: {e}")

    events = st.session_state.get("cal_events", [])
    if events:
        st.markdown("<div class='claude-card-title'>📅 Catalyst Calendar Events</div>", unsafe_allow_html=True)
        df_ev = pd.DataFrame(events)
        st.dataframe(df_ev, use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming calendar events detected for specified tickers.")
else:
    st.info("Enter tickers in the sidebar and click 'Load Market Calendar' to scan dates.")
