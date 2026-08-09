"""
MarketPulse — Streamlit Dashboard UI
Claude-themed financial intelligence workspace powered by LangGraph.
"""

from datetime import datetime
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.theme import (
    CLAUDE_COLORS,
    apply_claude_theme,
    get_claude_plotly_layout,
    render_claude_header,
)

st.set_page_config(
    page_title="MarketPulse — AI Financial Intelligence",
    page_icon="🧡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Claude Design System
apply_claude_theme()


def fmt_cap(cap):
    if not cap: return "N/A"
    if cap >= 1e12: return f"${cap/1e12:.2f}T"
    if cap >= 1e9:  return f"${cap/1e9:.2f}B"
    if cap >= 1e6:  return f"${cap/1e6:.2f}M"
    return f"${cap:,.0f}"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style='text-align:center;padding:0.8rem 0 1.2rem 0;'>
            <div style='font-size:2.2rem;margin-bottom:0.2rem;'>🧡</div>
            <div style='color:{CLAUDE_COLORS["terracotta"]};font-family:Lora,serif;font-weight:600;font-size:1.35rem;letter-spacing:-0.02em;'>MarketPulse</div>
            <div style='color:{CLAUDE_COLORS["text_secondary"]};font-size:0.76rem;margin-top:0.15rem;'>Claude-Powered Agentic Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 🎯 Analysis Target")
    ticker_input = st.text_input("Stock Ticker", value="AAPL", placeholder="e.g., AAPL, TSLA, NVDA").strip().upper()
    company_input = st.text_input("Company Name (optional)", placeholder="Auto-resolved if empty").strip()
    depth = st.selectbox("Analysis Depth", ["quick", "standard", "deep"], index=1,
        format_func=lambda x: {"quick": "⚡ Quick (5d)", "standard": "📊 Standard (1mo)", "deep": "🔍 Deep (3mo)"}[x])
    
    st.markdown("---")
    st.markdown("### ⚙️ LLM Provider & Model")
    llm_provider = st.selectbox("LLM Provider", ["openai", "google"])
    model_map = {
        "openai": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "google": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
    }
    llm_model = st.selectbox("Model", model_map[llm_provider])

    st.markdown("---")
    run_btn = st.button("🧡 Run Multi-Agent Pipeline", use_container_width=True)
    st.markdown(
        f"""
        <div style='color:{CLAUDE_COLORS["text_muted"]};font-size:0.72rem;text-align:center;margin-top:1rem;line-height:1.4;'>
            Powered by <strong>LangGraph</strong> + <strong>LangChain</strong><br>
            Autonomous 7-Agent Market Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Main Header ────────────────────────────────────────────────────────────────
render_claude_header(
    title="MarketPulse AI",
    subtitle="Autonomous Financial Intelligence Pipeline — Powered by LangGraph & Claude Theme System",
    icon="🧡",
)

if "result" not in st.session_state:
    st.session_state.result = None

if run_btn:
    if not ticker_input:
        st.error("Please enter a ticker symbol.")
    else:
        os.environ["LLM_PROVIDER"] = llm_provider
        os.environ["LLM_MODEL"] = llm_model
        with st.spinner(f"🤖 Agents executing analysis workflow for {ticker_input}…"):
            try:
                from graph.workflow import run_analysis
                st.session_state.result = run_analysis(ticker=ticker_input, company_name=company_input, analysis_depth=depth)
                st.success(f" Analysis complete for {st.session_state.result.get('company_name', ticker_input)}!")
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                st.session_state.result = None

result = st.session_state.result

if result:
    stock = result.get("stock_summary", {})
    ticker = result.get("ticker", "")
    cname = result.get("company_name", ticker)
    sent = result.get("overall_sentiment", "Neutral")
    risk = result.get("risk_level", "Medium")
    conf = result.get("sentiment_confidence", 0.0)
    chg = stock.get("change_pct", 0)

    sent_badge = {"bullish": "badge-bullish", "bearish": "badge-bearish", "neutral": "badge-neutral"}.get(sent.lower(), "badge-neutral")
    risk_badge = {"low": "badge-bullish", "medium": "badge-neutral", "high": "badge-bearish", "critical": "badge-bearish"}.get(risk.lower(), "badge-neutral")

    st.markdown(
        f"""
        <div style='margin-bottom: 1.2rem;'>
            <h2 style='color:{CLAUDE_COLORS["text_primary"]};margin:0;display:inline-block;font-size:1.8rem;'>
                {cname} <span style='color:{CLAUDE_COLORS["text_secondary"]};font-size:1.1rem;font-weight:400;'>({ticker})</span>
            </h2>
            <div style='margin-top: 0.5rem;'>
                <span class='claude-badge {sent_badge}'>📊 {sent} ({conf:.0%} Conf)</span> &nbsp;
                <span class='claude-badge {risk_badge}'>⚠️ {risk} Risk</span> &nbsp;
                <span class='claude-badge badge-terracotta'>⚡ {depth.capitalize()} Depth</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Metric Cards
    cols = st.columns(6)
    ms = [
        ("💰 Price", f"${stock.get('current_price', 0):.2f}", f"{chg:+.2f}%"),
        ("🏢 Mkt Cap", fmt_cap(stock.get("market_cap", 0)), None),
        ("📊 PE Ratio", str(stock.get("pe_ratio", "N/A")), None),
        ("🔄 Beta", str(stock.get("beta", "N/A")), None),
        ("📈 52W High", f"${stock.get('52w_high', 0):.2f}", None),
        ("📉 52W Low", f"${stock.get('52w_low', 0):.2f}", None),
    ]
    for col, (lbl, val, ch) in zip(cols, ms):
        with col:
            ch_style = f"color:{CLAUDE_COLORS['emerald']};" if "+" in (ch or "") else f"color:{CLAUDE_COLORS['rose']};"
            ch_html = f"<div style='font-size:0.8rem;font-weight:600;{ch_style}'>{ch}</div>" if ch else ""
            st.markdown(
                f"""
                <div class='claude-metric-card'>
                    <div class='claude-metric-lbl'>{lbl}</div>
                    <div class='claude-metric-val'>{val}</div>
                    {ch_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='claude-card-title'>📈 Price History (Candlestick & OHLC)</div>", unsafe_allow_html=True)
        ph = result.get("price_history", [])
        if ph and "error" not in ph[0]:
            df = pd.DataFrame(ph)
            df["date"] = pd.to_datetime(df["date"])
            fig = go.Figure(
                go.Candlestick(
                    x=df["date"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    increasing_line_color=CLAUDE_COLORS["emerald"],
                    decreasing_line_color=CLAUDE_COLORS["rose"],
                    name="OHLC",
                )
            )
            layout = get_claude_plotly_layout(height=320)
            layout["xaxis_rangeslider_visible"] = False
            fig.update_layout(layout)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Price history chart unavailable for this asset.")

    with c2:
        st.markdown("<div class='claude-card-title'>🧠 Sentiment Score Breakdown</div>", unsafe_allow_html=True)
        ss = result.get("sentiment_scores", [])
        if ss:
            cnts = {"Bullish": 0, "Bearish": 0, "Neutral": 0}
            for s in ss:
                cnts[s.get("sentiment", "Neutral")] = cnts.get(s.get("sentiment", "Neutral"), 0) + 1
            fig2 = go.Figure(
                go.Pie(
                    labels=list(cnts.keys()),
                    values=list(cnts.values()),
                    hole=0.6,
                    marker=dict(colors=[CLAUDE_COLORS["emerald"], CLAUDE_COLORS["rose"], CLAUDE_COLORS["gold"]]),
                    textinfo="label+percent",
                    textfont=dict(color=CLAUDE_COLORS["text_primary"], size=11),
                )
            )
            fig2.update_layout(get_claude_plotly_layout(height=320))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown(
                f"""
                <div style='text-align:center;padding:3rem 1rem;'>
                    <span class='claude-badge {sent_badge}' style='font-size:1.1rem;'>{sent}</span>
                    <div style='color:{CLAUDE_COLORS["text_secondary"]};margin-top:0.8rem;font-size:0.85rem;'>Confidence: {conf:.0%}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Risk Flags & Insights
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("<div class='claude-card-title'>⚠️ Risk Flags & Vulnerabilities</div>", unsafe_allow_html=True)
        flags = result.get("risk_flags", [])
        if flags:
            for f in flags:
                st.markdown(f"<div class='claude-flag-risk'>🔴 {f}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='claude-flag-insight'> No critical risk flags detected.</div>", unsafe_allow_html=True)

    with r2:
        st.markdown("<div class='claude-card-title'>💡 Key Market Insights</div>", unsafe_allow_html=True)
        ins = result.get("key_insights", [])
        if ins:
            for i in ins:
                st.markdown(f"<div class='claude-flag-insight'>✦ {i}</div>", unsafe_allow_html=True)
        else:
            st.info("No insights generated for this stock.")

    st.markdown("<br>", unsafe_allow_html=True)

    # News & Investment Report
    n1, n2 = st.columns([1, 1])
    with n1:
        st.markdown("<div class='claude-card-title'>📰 Financial News Feed</div>", unsafe_allow_html=True)
        for art in result.get("raw_news", [])[:5]:
            if "error" in art: continue
            st.markdown(
                f"""
                <div class='claude-news-item'>
                    <div style='font-weight:600;font-size:0.9rem;'>
                        <a href='{art.get('url','#')}' target='_blank' style='color:{CLAUDE_COLORS["terracotta"]};text-decoration:none;'>
                            {art.get('title','N/A')}
                        </a>
                    </div>
                    <div style='color:{CLAUDE_COLORS["text_secondary"]};font-size:0.75rem;margin-top:0.3rem;'>
                        📰 {art.get('source','Unknown')} · 📅 {str(art.get('publishedAt',''))[:10]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with n2:
        st.markdown("<div class='claude-card-title'>📄 Investment Intelligence Report</div>", unsafe_allow_html=True)
        rpt = result.get("final_report", "")
        if rpt:
            with st.expander("📋 View Executive Synthesis", expanded=True):
                st.markdown(rpt)
            st.download_button(
                "⬇️ Download Markdown Report (.md)",
                data=rpt,
                file_name=f"{ticker}_{datetime.now().strftime('%Y%m%d')}_marketpulse.md",
                mime="text/markdown",
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive Claude Copilot Assistant
    st.markdown("<div class='claude-card-title'>💬 Claude Co-Pilot — Ask Questions About Analysis</div>", unsafe_allow_html=True)
    user_q = st.text_input("Ask MarketPulse AI a question about this ticker (e.g., 'What is the risk ratio?')", key="copilot_q")
    if user_q:
        st.markdown(
            f"""
            <div class='claude-card' style='border-left:3px solid {CLAUDE_COLORS["terracotta"]};margin-top:0.5rem;'>
                <strong>🤖 MarketPulse Copilot:</strong> Based on our multi-agent analysis for {cname} ({ticker}), 
                the overall sentiment is <strong>{sent}</strong> with a risk assessment level of <strong>{risk}</strong>.
                Key risk factors include: {", ".join(result.get("risk_flags", ["None"]))}.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🤖 Agent Execution Logs & Messages"):
        for m in result.get("messages", []):
            st.code(m, language=None)

else:
    # Default Ready Screen
    st.markdown(
        f"""
        <div style='text-align:center;padding:3.5rem 2rem;'>
            <div style='font-size:3.5rem;margin-bottom:1rem;'>🧡</div>
            <h2 style='color:{CLAUDE_COLORS["text_primary"]};font-family:Lora,serif;'>Ready for Autonomous Financial Intelligence</h2>
            <p style='color:{CLAUDE_COLORS["text_secondary"]};max-width:600px;margin:0 auto 2.5rem auto;'>
                Enter a stock ticker in the sidebar and click <strong style='color:{CLAUDE_COLORS["terracotta"]};'>Run Multi-Agent Pipeline</strong> to launch news collection, sentiment scoring, technical analysis, and risk evaluation.
            </p>
            <div style='display:flex;justify-content:center;gap:1.2rem;flex-wrap:wrap;'>
                <div class='claude-card' style='width:170px;'>
                    <div style='font-size:1.6rem;'>📰</div>
                    <div style='color:{CLAUDE_COLORS["terracotta"]};font-weight:600;margin:0.4rem 0;'>News Agent</div>
                    <div style='font-size:0.76rem;color:{CLAUDE_COLORS["text_secondary"]};'>Scrapes &amp; digests market news</div>
                </div>
                <div class='claude-card' style='width:170px;'>
                    <div style='font-size:1.6rem;'>🧠</div>
                    <div style='color:{CLAUDE_COLORS["terracotta"]};font-weight:600;margin:0.4rem 0;'>Sentiment Agent</div>
                    <div style='font-size:0.76rem;color:{CLAUDE_COLORS["text_secondary"]};'>LLM article sentiment scoring</div>
                </div>
                <div class='claude-card' style='width:170px;'>
                    <div style='font-size:1.6rem;'>📈</div>
                    <div style='color:{CLAUDE_COLORS["terracotta"]};font-weight:600;margin:0.4rem 0;'>Stock Data Agent</div>
                    <div style='font-size:0.76rem;color:{CLAUDE_COLORS["text_secondary"]};'>Real-time price &amp; OHLC metrics</div>
                </div>
                <div class='claude-card' style='width:170px;'>
                    <div style='font-size:1.6rem;'>⚠️</div>
                    <div style='color:{CLAUDE_COLORS["terracotta"]};font-weight:600;margin:0.4rem 0;'>Risk Analyst</div>
                    <div style='font-size:0.76rem;color:{CLAUDE_COLORS["text_secondary"]};'>Risk flags &amp; insights</div>
                </div>
                <div class='claude-card' style='width:170px;'>
                    <div style='font-size:1.6rem;'>📄</div>
                    <div style='color:{CLAUDE_COLORS["terracotta"]};font-weight:600;margin:0.4rem 0;'>Report Agent</div>
                    <div style='font-size:0.76rem;color:{CLAUDE_COLORS["text_secondary"]};'>Executive Markdown reports</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
