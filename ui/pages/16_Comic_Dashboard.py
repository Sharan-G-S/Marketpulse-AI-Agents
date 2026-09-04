"""
MarketPulse — Graphic Novel & Comic Financial Dashboard
Displays AI agent analysis as an interactive pop-art comic strip story.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.comic_theme import COMIC_COLORS, apply_comic_theme, get_comic_plotly_layout, render_comic_header, render_comic_sfx
from agents.comic_agent import generate_comic_storyboard

st.set_page_config(page_title="Comic Dashboard — MarketPulse", page_icon="💥", layout="wide")
apply_comic_theme()

render_comic_header(
    title="THE ADVENTURES OF AGENT MARKETPULSE!",
    subtitle="Interactive Graphic Novel Financial Intelligence & AI Agent Storytelling",
    icon="💥"
)

st.sidebar.markdown("### ⚡ HERO CONTROLS")
ticker = st.sidebar.text_input("TARGET ASSET TICKER", value="NVDA").strip().upper()
launch_btn = st.sidebar.button("🚀 LAUNCH AGENT MISSION", use_container_width=True)

if launch_btn or "comic_mission_res" in st.session_state:
    if launch_btn and ticker:
        with st.spinner(f"⚡ AGENTS IN ACTION FOR {ticker}...!"):
            try:
                from graph.workflow import run_analysis
                res = run_analysis(ticker=ticker, analysis_depth="quick")
                st.session_state.comic_mission_res = res
            except Exception as e:
                st.error(f"Mission failed: {e}")

    res = st.session_state.get("comic_mission_res", {})
    if res:
        stock = res.get("stock_summary", {})
        cname = res.get("company_name", ticker)
        sent = res.get("overall_sentiment", "Neutral")
        risk = res.get("risk_level", "Medium")

        st.markdown(
            f"""
            <div class="comic-bubble" style="background:#ffffff;border-color:{COMIC_COLORS['red']};">
                <span class="comic-starburst">MISSION REPORT: {cname} ({ticker})</span>
                <div style="font-size:1.8rem;font-family:'Bangers',cursive;margin-top:0.6rem;">
                    PRICE: ${stock.get('current_price', 0):.2f} &nbsp;|&nbsp; SENTIMENT: {sent.upper()} &nbsp;|&nbsp; RISK: {risk.upper()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        panels = generate_comic_storyboard(res)

        col1, col2 = st.columns(2)
        for i, panel in enumerate(panels):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                st.markdown(
                    f"""
                    <div class="comic-bubble">
                        <div class="comic-card-title">{panel['panel']}: {panel['title']}</div>
                        <div style="font-size:1.05rem;font-weight:700;margin-bottom:0.4rem;">
                            "{panel['dialogue']}"
                        </div>
                        <div style="color:{COMIC_COLORS['text_muted']};font-size:0.85rem;">
                            {panel['narrative']}
                        </div>
                        <div style="margin-top:0.4rem;">
                            <span class="comic-starburst" style="font-size:0.9rem;padding:0.2rem 0.6rem;">
                                {panel['sound_effect']}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<div class='comic-card-title'>PANEL 5: 📈 PRICE HISTORY BATTLE CHART</div>", unsafe_allow_html=True)
        render_comic_sfx("KAPOW!")
        ph = res.get("price_history", [])
        if ph and "error" not in ph[0]:
            df = pd.DataFrame(ph)
            fig = go.Figure(go.Candlestick(
                x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
                increasing_line_color=COMIC_COLORS["green"],
                decreasing_line_color=COMIC_COLORS["red"],
            ))
            fig.update_layout(get_comic_plotly_layout(height=320, title=f"{ticker} Price Action"))
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Enter a stock ticker in the sidebar and click 'LAUNCH AGENT MISSION'!")
