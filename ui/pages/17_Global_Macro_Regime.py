"""
MarketPulse — Global Macro Regime & World Market Tracker Page
Monitors live global indices (S&P 500, Nasdaq, FTSE 100, Nikkei 225, Nifty 50) and forex rates.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import CLAUDE_COLORS, apply_theme_by_name, render_claude_header, get_claude_plotly_layout
from tools.world_market_scanner import scan_world_markets
from tools.forex_converter import convert_currency

st.set_page_config(page_title="Global Macro Regime — MarketPulse", page_icon="🌍", layout="wide")
apply_theme_by_name("claude")

render_claude_header(
    title="Global Macro Regime & World Market Tracker",
    subtitle="Cross-Border Market Sentiment Scanner, Major Indices, & Forex Currency Matrix",
    icon="🌍"
)

with st.spinner("🌐 Scanning global market indices across Americas, Europe, & Asia-Pacific..."):
    data = scan_world_markets()

regime = data.get("macro_regime", "Neutral Macro")
indices = data.get("indices", {})

badge_color = "badge-bullish" if "Bullish" in regime else ("badge-bearish" if "Bearish" in regime else "badge-neutral")

st.markdown(
    f"""
    <div style="margin-bottom:1.5rem;">
        <span class="claude-badge {badge_color}" style="font-size:1.1rem;padding:0.4rem 1.1rem;">
            🌐 GLOBAL MACRO REGIME: {regime.upper()}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Render Global Index Metric Cards
cols = st.columns(len(indices) if indices else 1)
for col, (symbol, idx_data) in zip(cols, indices.items()):
    chg = idx_data.get("change_pct", 0.0)
    chg_str = f"{chg:+.2f}%"
    chg_color = f"color:{CLAUDE_COLORS['emerald']};" if chg >= 0 else f"color:{CLAUDE_COLORS['rose']};"
    with col:
        st.markdown(
            f"""
            <div class="claude-metric-card">
                <div class="claude-metric-lbl">{idx_data.get('region')} · {idx_data.get('name')}</div>
                <div class="claude-metric-val">${idx_data.get('price', 0):,.2f}</div>
                <div style="font-size:0.85rem;font-weight:700;{chg_color}">{chg_str}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# Forex Currency Converter Section
c1, c2 = st.columns([1, 1])
with c1:
    st.markdown("<div class='claude-card-title'>💱 Multi-Currency Valuation Converter</div>", unsafe_allow_html=True)
    amt = st.number_input("Amount to Convert", value=1000.0, step=100.0)
    col_a, col_b = st.columns(2)
    with col_a:
        from_curr = st.selectbox("From Currency", ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD"])
    with col_b:
        to_curr = st.selectbox("To Currency", ["EUR", "USD", "GBP", "JPY", "INR", "CAD", "AUD"])

    converted = convert_currency(amt, from_curr=from_curr, to_curr=to_curr)
    st.markdown(
        f"""
        <div class="claude-card" style="text-align:center;margin-top:1rem;">
            <div style="color:{CLAUDE_COLORS['text_secondary']};font-size:0.85rem;">CONVERTED VALUE</div>
            <div style="font-size:2.2rem;font-weight:700;color:{CLAUDE_COLORS['terracotta']};">
                {converted:,.2f} {to_curr}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown("<div class='claude-card-title'>📊 Global Indices Performance Matrix</div>", unsafe_allow_html=True)
    df = pd.DataFrame([
        {"Index": v["name"], "Region": v["region"], "Price": v["price"], "Change %": v["change_pct"]}
        for v in indices.values()
    ])
    fig = go.Figure(go.Bar(
        x=df["Index"],
        y=df["Change %"],
        marker_color=[CLAUDE_COLORS["emerald"] if x >= 0 else CLAUDE_COLORS["rose"] for x in df["Change %"]],
    ))
    fig.update_layout(get_claude_plotly_layout(height=280, title="Daily % Change Across World Markets"))
    st.plotly_chart(fig, use_container_width=True)
