"""
Portfolio Performance Page — Streamlit UI for MarketPulse.
Track P&L, position weights, & sector asset allocation in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS, get_claude_plotly_layout
from tools.portfolio_performance import compute_portfolio, sector_allocation

st.set_page_config(page_title="Portfolio Performance — MarketPulse", page_icon="💼", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Portfolio Performance & Asset Allocation",
    subtitle="Track unrealized P&L, position weights, sector exposure, and total portfolio valuation",
    icon="💼"
)

st.sidebar.markdown("### 🧺 Portfolio Holdings Entry")
num_pos = st.sidebar.number_input("Number of Positions", min_value=1, max_value=10, value=3)

positions = []
for i in range(num_pos):
    col_t, col_s, col_c = st.sidebar.columns([1, 1, 1])
    tk = col_t.text_input(f"Ticker #{i+1}", value=["AAPL", "MSFT", "NVDA"][i % 3], key=f"tk_{i}").strip().upper()
    sh = col_s.number_input(f"Shares #{i+1}", min_value=1.0, value=[10.0, 5.0, 15.0][i % 3], key=f"sh_{i}")
    cp = col_c.number_input(f"Cost/Sh #{i+1}", min_value=1.0, value=[150.0, 300.0, 100.0][i % 3], key=f"cp_{i}")
    positions.append({"ticker": tk, "shares": sh, "avg_cost": cp})

calc_btn = st.sidebar.button("💼 Evaluate Portfolio", use_container_width=True)

if calc_btn or "port_res" in st.session_state:
    if calc_btn:
        with st.spinner("Fetching live market prices & computing portfolio P&L..."):
            try:
                res = compute_portfolio(positions)
                st.session_state.port_res = res
            except Exception as e:
                st.error(f"Portfolio calculation failed: {e}")
                st.session_state.port_res = {}

    res = st.session_state.get("port_res", {})
    if res and "error" not in res:
        tot_val = res.get("total_market_value", 0)
        tot_pnl = res.get("total_unrealised_pnl", 0)
        pnl_pct = res.get("total_pnl_pct", 0)

        # Overview Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Market Value", f"${tot_val:,.2f}")
        m2.metric("Unrealised P&L ($)", f"${tot_pnl:,.2f}")
        m3.metric("Unrealised P&L (%)", f"{pnl_pct:+.2f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("<div class='claude-card-title'>📊 Sector Allocation Breakdown</div>", unsafe_allow_html=True)
            sec_alloc = sector_allocation(res.get("positions", []))
            if sec_alloc:
                fig = go.Figure(go.Pie(
                    labels=list(sec_alloc.keys()),
                    values=list(sec_alloc.values()),
                    hole=0.55,
                    marker=dict(colors=[CLAUDE_COLORS["terracotta"], CLAUDE_COLORS["emerald"], CLAUDE_COLORS["gold"], CLAUDE_COLORS["blue"]]),
                    textinfo="label+percent",
                    textfont=dict(color=CLAUDE_COLORS["text_primary"]),
                ))
                fig.update_layout(get_claude_plotly_layout(height=300))
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("<div class='claude-card-title'>📋 Position Breakdown Table</div>", unsafe_allow_html=True)
            df_pos = pd.DataFrame(res.get("positions", []))
            st.dataframe(df_pos, use_container_width=True, hide_index=True)
else:
    st.info("Enter holdings in the sidebar and click 'Evaluate Portfolio' to start.")
