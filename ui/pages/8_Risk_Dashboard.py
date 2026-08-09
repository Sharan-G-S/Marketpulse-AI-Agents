"""
Risk Dashboard — Streamlit Page for MarketPulse.
Computes and displays risk metrics (Sharpe, Sortino, Max Drawdown, VaR, Calmar) in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS
from tools.risk_metrics import compute_risk_metrics
from tools.risk_metrics_helpers import risk_metrics_to_dict

st.set_page_config(page_title="Risk Dashboard — MarketPulse", page_icon="⚠️", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Portfolio & Asset Risk Analytics",
    subtitle="Evaluate downside Risk-at-Value (VaR), Sharpe ratios, maximum drawdown, and Sortino ratios",
    icon="⚠️"
)

st.sidebar.markdown("### ⚙️ Risk Calculation Settings")
tickers_input = st.sidebar.text_input("Tickers (comma separated)", value="AAPL, TSLA, NVDA")
days = st.sidebar.slider("Historical Period (Days)", min_value=30, max_value=365, value=90)
calc_btn = st.sidebar.button("⚠️ Calculate Risk Profile", use_container_width=True)

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

if calc_btn or "risk_results" in st.session_state:
    if calc_btn:
        with st.spinner(f"Computing risk metrics across {len(tickers)} assets..."):
            results = []
            for tk in tickers:
                try:
                    rm = compute_risk_metrics(tk, days=days)
                    results.append(risk_metrics_to_dict(rm))
                except Exception as e:
                    st.warning(f"Could not compute risk for {tk}: {e}")
            st.session_state.risk_results = results

    risk_list = st.session_state.get("risk_results", [])
    if risk_list:
        df_risk = pd.DataFrame(risk_list)
        st.markdown("<div class='claude-card-title'>📊 Cross-Asset Downside Risk Comparison</div>", unsafe_allow_html=True)
        st.dataframe(df_risk, use_container_width=True, hide_index=True)
else:
    st.info("Enter tickers in the sidebar and click 'Calculate Risk Profile' to begin.")
