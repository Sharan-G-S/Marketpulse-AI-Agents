"""
MarketPulse Streamlit Pages — About Page
Project architecture, multi-agent pipeline details, tech stack, and version history.
"""

from datetime import datetime
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS

st.set_page_config(page_title="MarketPulse — About", page_icon="ℹ️", layout="wide")
apply_claude_theme()

render_claude_header(
    title="About MarketPulse AI",
    subtitle="State-of-the-Art Autonomous Multi-Agent Financial Intelligence Platform",
    icon="ℹ️"
)

st.markdown(f"""
<div class='claude-card' style='margin-bottom:1.5rem;'>
    <div style='font-size:1.1rem;font-weight:600;color:{CLAUDE_COLORS["terracotta"]};font-family:Lora,serif;'>🧡 Autonomous Multi-Agent Architecture</div>
    <p style='color:{CLAUDE_COLORS["text_secondary"]};margin-top:0.5rem;line-height:1.6;'>
        <strong>MarketPulse</strong> orchestrates 7 autonomous AI agents connected via a directed <strong>LangGraph StateGraph</strong> workflow.
        It systematically collects financial news, fetches price action OHLC data, evaluates sentiment scores via LLMs, analyzes risk indicators, builds watchlists, computes portfolio health metrics, and generates publication-ready investment reports.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='claude-card-title'>🤖 Multi-Agent Orchestration Pipeline</div>", unsafe_allow_html=True)
agents = [
    ("📰", "News Fetcher", "Scrapes financial news & headlines via NewsAPI"),
    ("📈", "Stock Analyst", "Fetches real-time price & historical OHLC data"),
    ("🧠", "Sentiment Engine", "Per-article & overall market sentiment scoring"),
    ("⚠️", "Risk Analyst", "Cross-checks data for market & downside risk flags"),
    ("📋", "Watchlist Agent", "Monitors ticker watchlist metrics & price targets"),
    ("🧺", "Portfolio Tracker", "Computes health score, beta, & asset allocation"),
    ("📄", "Report Synthesizer", "Generates comprehensive executive reports"),
]
cols = st.columns(7)
for col, (icon, name, desc) in zip(cols, agents):
    with col:
        st.markdown(f"""
        <div class='claude-card' style='text-align:center;padding:0.9rem 0.6rem;height:100%;'>
            <div style='font-size:1.6rem;'>{icon}</div>
            <div style='color:{CLAUDE_COLORS["terracotta"]};font-weight:600;font-size:0.85rem;margin:0.3rem 0;'>{name}</div>
            <div style='color:{CLAUDE_COLORS["text_secondary"]};font-size:0.72rem;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='claude-card-title'>🛠️ Technology Stack</div>", unsafe_allow_html=True)
stack = [
    ("🔗", "LangGraph", "Directed multi-agent state orchestration graph"),
    ("⛓️", "LangChain", "LLM prompts, tool wrappers, output parsers"),
    ("🤖", "Claude / GPT / Gemini", "LLM backbone options for intelligence"),
    ("📊", "yfinance", "Real-time stock quotes, OHLC history & info"),
    ("📰", "NewsAPI", "Global financial & business news feeds"),
    ("🖥️", "Streamlit", "Claude-themed interactive web UI"),
    ("📉", "Plotly", "Interactive dark-mode charts & heatmaps"),
    ("⚡", "Caching Engine", "In-memory & disk TTL performance cache"),
]
cols2 = st.columns(4)
for i, (icon, name, desc) in enumerate(stack):
    with cols2[i % 4]:
        st.markdown(f"""
        <div class='claude-card' style='margin-bottom:0.75rem;'>
            <div style='font-size:1.4rem;'>{icon} <strong style='color:{CLAUDE_COLORS["text_primary"]};font-size:0.95rem;'>{name}</strong></div>
            <div style='color:{CLAUDE_COLORS["text_secondary"]};font-size:0.78rem;margin-top:0.2rem;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='claude-card-title'>📦 Version History</div>", unsafe_allow_html=True)
st.markdown("""
| Version | Release Date | Key Innovations |
| :--- | :--- | :--- |
| **v2.0.0** | 2026-08-09 | Production overhaul: Claude UI theme system, yfinance & news TTL caching, Efficient Frontier Portfolio Optimizer, multi-ticker AI synthesis, 500+ unit tests |
| **v1.7.4** | 2026-05-15 | Stochastic Oscillator, ATR, Free Cash Flow analysis, HTML color formatting |
| **v1.7.0** | 2026-05-12 | Diversification Scorer, Earnings Surprise, MA Crossover, Data Quality Validator |
| **v1.0.0** | 2026-04-28 | Initial 5-agent LangGraph pipeline release |
""")

st.markdown("---")
st.markdown(f"<div style='color:{CLAUDE_COLORS['text_muted']};font-size:0.8rem;text-align:center;'>⚠️ <strong>Disclaimer:</strong> MarketPulse AI is designed strictly for educational and informational purposes and does not constitute official financial advice.</div>", unsafe_allow_html=True)
