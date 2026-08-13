"""
MarketPulse — Monte Carlo 10,000-Path Asset Return Simulator Page
Stochastic Geometric Brownian Motion (GBM) price path simulation & 95% VaR visualizer.
"""

import os
import sys
import streamlit as st
import numpy as np
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import CLAUDE_COLORS, apply_theme_by_name, render_claude_header, get_claude_plotly_layout
from tools.monte_carlo import run_monte_carlo_simulation

st.set_page_config(page_title="Monte Carlo Simulator — MarketPulse", page_icon="🎲", layout="wide")
apply_theme_by_name("claude")

render_claude_header(
    title="10,000-Path Monte Carlo Asset Return Simulator",
    subtitle="Stochastic Geometric Brownian Motion (GBM) Price Distribution & 95% VaR Calculator",
    icon="🎲"
)

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("<div class='claude-card-title'>⚙️ Simulation Controls</div>", unsafe_allow_html=True)
    price = st.number_input("Starting Asset Price ($)", value=150.0, step=5.0)
    drift = st.slider("Annual Drift Return (%)", min_value=-50.0, max_value=50.0, value=12.0) / 100.0
    vol = st.slider("Annual Volatility (%)", min_value=5.0, max_value=100.0, value=25.0) / 100.0
    days = st.slider("Trading Days Horizon", min_value=5, max_value=252, value=30)
    sims = st.selectbox("Number of Simulated Paths", [500, 1000, 2500, 5000], index=1)

    res = run_monte_carlo_simulation(price, annual_return=drift, annual_volatility=vol, days=days, num_simulations=sims)

    st.markdown(
        f"""
        <div class="claude-card" style="margin-top:1rem;">
            <div style="color:{CLAUDE_COLORS['text_secondary']};font-size:0.8rem;">ESTIMATED 95% VALUE AT RISK (VaR)</div>
            <div style="font-size:2rem;font-weight:700;color:{CLAUDE_COLORS['rose']};">{res.get('var_95_pct', 0):.2f}%</div>
            <div style="font-size:0.8rem;color:{CLAUDE_COLORS['text_secondary']};margin-top:0.3rem;">
                5th Percentile Price: <strong>${res.get('percentile_5th', 0):.2f}</strong><br>
                Median Projected Price: <strong>${res.get('median_final_price', 0):.2f}</strong><br>
                95th Percentile Price: <strong>${res.get('percentile_95th', 0):.2f}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown("<div class='claude-card-title'>📈 Simulated Price Trajectories (Sample Paths)</div>", unsafe_allow_html=True)
    # Generate sample paths for chart
    dt = 1.0 / 252.0
    np.random.seed(42)
    sample_sims = 30
    daily_rets = np.random.normal((drift - 0.5 * vol**2) * dt, vol * np.sqrt(dt), (days, sample_sims))
    paths = np.zeros((days + 1, sample_sims))
    paths[0] = price
    for t in range(1, days + 1):
        paths[t] = paths[t - 1] * np.exp(daily_rets[t - 1])

    fig = go.Figure()
    for i in range(sample_sims):
        fig.add_trace(go.Scatter(x=list(range(days + 1)), y=paths[:, i], mode="lines", opacity=0.3, showlegend=False))

    fig.update_layout(get_claude_plotly_layout(height=360, title=f"Stochastic Price Paths ({days} Days Horizon)"))
    st.plotly_chart(fig, use_container_width=True)
