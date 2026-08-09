"""
Compare Stocks — Streamlit Page for MarketPulse.
Side-by-side stock comparison, relative valuation, & ranking powered by Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS, get_claude_plotly_layout
from agents.comparison_agent import compare_tickers, score_label
from agents.comparison_helpers import format_comparison_table, format_rankings_summary, format_score_breakdown_table

st.set_page_config(page_title="Compare Stocks — MarketPulse", page_icon="⚖️", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Stock Comparison Engine",
    subtitle="Side-by-side fundamentals, valuation ratios, technical setup & multi-ticker AI scoring",
    icon="⚖️"
)

st.sidebar.markdown("### 🔍 Comparison Tickers")
raw_input = st.sidebar.text_input("Enter 2 to 5 Tickers (comma-separated)", value="AAPL, MSFT, NVDA")
cmp_btn = st.sidebar.button("⚖️ Run Side-by-Side Comparison", use_container_width=True)

tickers = [t.strip().upper() for t in raw_input.split(",") if t.strip()]

if cmp_btn or "cmp_result" in st.session_state:
    if cmp_btn:
        if len(tickers) < 2:
            st.error("Please enter at least 2 tickers to compare.")
        else:
            with st.spinner(f"Comparing {', '.join(tickers)} across fundamental & sentiment metrics..."):
                try:
                    st.session_state.cmp_result = compare_tickers(tickers)
                except Exception as e:
                    st.error(f"Comparison failed: {e}")
                    st.session_state.cmp_result = None

    cmp_res = st.session_state.get("cmp_result")
    if cmp_res:
        winner = cmp_res.get("winner", "N/A")
        rankings = cmp_res.get("rankings", [])

        st.markdown(
            f"""
            <div class='claude-card' style='border:2px solid {CLAUDE_COLORS["terracotta"]};text-align:center;padding:1.5rem;margin-bottom:1.5rem;'>
                <div style='font-size:1.8rem;'>🏆</div>
                <div style='font-size:1.4rem;font-weight:700;color:{CLAUDE_COLORS["terracotta"]};font-family:Lora,serif;'>
                    Top Recommendation: {winner}
                </div>
                <div style='color:{CLAUDE_COLORS["text_secondary"]};font-size:0.88rem;margin-top:0.3rem;'>
                    Highest relative composite score based on valuation, growth, momentum, and risk balance.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Render Score Comparison Chart
        if rankings:
            df_rank = pd.DataFrame(rankings)
            fig = go.Figure(go.Bar(
                x=df_rank["ticker"],
                y=df_rank["composite_score"],
                marker_color=CLAUDE_COLORS["terracotta"],
                text=df_rank["composite_score"].round(1),
                textposition="outside",
            ))
            fig.update_layout(get_claude_plotly_layout(height=320, title="Composite AI Score (0-100)"))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='claude-card-title'>📊 Side-by-Side Comparison Matrix</div>", unsafe_allow_html=True)
        items = cmp_res.get("comparisons", [])
        if items:
            df_items = pd.DataFrame(items)
            st.dataframe(df_items, use_container_width=True)
else:
    st.info("Enter tickers in the sidebar and click 'Run Side-by-Side Comparison' to start.")
