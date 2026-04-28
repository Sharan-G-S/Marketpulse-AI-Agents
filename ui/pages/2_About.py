"""
MarketPulse Streamlit Pages — About Page
Project info, team, and tech stack overview.
"""

import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

st.set_page_config(page_title="MarketPulse — About", page_icon="ℹ️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
section[data-testid="stSidebar"]{background:#0d1117;}
.tech-card{background:rgba(17,24,39,.8);border:1px solid rgba(99,179,237,.15);border-radius:12px;padding:1.2rem;text-align:center;margin-bottom:.75rem;}
.tech-name{color:#90cdf4;font-weight:700;font-size:1rem;margin:.4rem 0;}
.tech-desc{color:#718096;font-size:.8rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("## ℹ️ About MarketPulse")
st.markdown("""
**MarketPulse** is an autonomous multi-agent financial intelligence system built with
**LangGraph** and **LangChain**. It orchestrates five specialized AI agents through a
directed state graph to deliver comprehensive investment insights in seconds.
""")

st.markdown("---")
st.markdown("### 🤖 Agent Pipeline")
agents = [
    ("📰", "News Agent",      "Fetches the latest financial news via NewsAPI"),
    ("📈", "Stock Agent",     "Real-time OHLCV market data via yfinance"),
    ("🧠", "Sentiment Agent", "LLM-powered per-article sentiment scoring"),
    ("⚠️", "Risk Agent",      "Cross-references data to flag investment risks"),
    ("📄", "Report Agent",    "Generates professional investment reports"),
]
cols = st.columns(5)
for col, (icon, name, desc) in zip(cols, agents):
    with col:
        st.markdown(f"<div class='tech-card'><div style='font-size:1.8rem;'>{icon}</div><div class='tech-name'>{name}</div><div class='tech-desc'>{desc}</div></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🛠️ Tech Stack")
stack = [
    ("🔗", "LangGraph",   "Multi-agent state machine orchestration"),
    ("⛓️", "LangChain",   "LLM chains, prompts, tool wrappers"),
    ("🤖", "OpenAI/Gemini","GPT-4o-mini or Gemini 1.5 Flash LLM backbone"),
    ("📊", "yfinance",    "Free real-time & historical stock data"),
    ("📰", "NewsAPI",     "Financial news article fetching"),
    ("🖥️", "Streamlit",   "Interactive dashboard UI"),
    ("📉", "Plotly",      "Candlestick charts & visualizations"),
    ("🧠", "FAISS",       "Vector store for memory & retrieval"),
]
cols2 = st.columns(4)
for i, (icon, name, desc) in enumerate(stack):
    with cols2[i % 4]:
        st.markdown(f"<div class='tech-card'><div style='font-size:1.5rem;'>{icon}</div><div class='tech-name'>{name}</div><div class='tech-desc'>{desc}</div></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("> ⚠️ **Disclaimer:** MarketPulse is for educational purposes only and does not constitute financial advice.")
