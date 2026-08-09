"""
MarketPulse — CSV Data Export Page
Provides a Streamlit UI for downloading portfolio positions, watchlist data,
and triggered alerts as CSV files in Claude design theme.
"""

import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS
from tools.csv_export import export_alerts_csv, export_portfolio_csv, export_watchlist_csv

st.set_page_config(page_title="Export Data — MarketPulse", page_icon="📥", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Data Export Suite",
    subtitle="Export portfolio positions, watchlist snapshots, and triggered alerts as CSV files",
    icon="📥"
)


def _get(key: str, default=None):
    return st.session_state.get(key, default)


st.markdown("<div class='claude-card-title'>📊 Portfolio Positions</div>", unsafe_allow_html=True)
portfolio_result = _get("portfolio_result")
positions = (portfolio_result or {}).get("positions", [])

if positions:
    valid = [p for p in positions if p.get("market_value") is not None]
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"**Total Market Value:** ${(portfolio_result or {}).get('total_market_value', 0):,.2f}  \n"
            f"**Unrealised P&L:** ${(portfolio_result or {}).get('total_unrealised_pnl', 0):,.2f}  \n"
            f"**Diversification:** {(portfolio_result or {}).get('diversification_label', '—')}"
        )
    with col2:
        csv_data = export_portfolio_csv(valid)
        st.download_button(
            label="⬇ Download Portfolio CSV",
            data=csv_data,
            file_name="marketpulse_portfolio.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_portfolio",
        )
else:
    st.info("No portfolio data found in active session. Execute an analysis on the main dashboard to populate positions.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='claude-card-title'>📋 Watchlist Snapshot</div>", unsafe_allow_html=True)

stock_summary = _get("stock_summary", {})
watchlist = stock_summary.get("watchlist", []) if isinstance(stock_summary, dict) else []

if watchlist:
    valid_wl = [w for w in watchlist if "error" not in w]
    col1, col2 = st.columns([3, 1])
    with col1:
        if valid_wl:
            tickers_str = ", ".join(w.get("ticker", "?") for w in valid_wl)
            st.markdown(f"**Tracked Tickers:** {tickers_str}")
    with col2:
        csv_data = export_watchlist_csv(valid_wl)
        st.download_button(
            label="⬇ Download Watchlist CSV",
            data=csv_data,
            file_name="marketpulse_watchlist.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_watchlist",
        )
else:
    st.info("No active watchlist snapshot found. Run a stock analysis to generate watchlist metrics.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='claude-card-title'>🚨 Triggered Alerts</div>", unsafe_allow_html=True)

alerts = stock_summary.get("alerts", []) if isinstance(stock_summary, dict) else []

if alerts:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"{len(alerts)} alert(s) ready for export.")
    with col2:
        csv_data = export_alerts_csv(alerts)
        st.download_button(
            label="⬇ Download Alerts CSV",
            data=csv_data,
            file_name="marketpulse_alerts.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_alerts",
        )
else:
    st.info("No alerts generated in current session.")
