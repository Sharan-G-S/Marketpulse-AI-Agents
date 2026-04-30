"""
MarketPulse — Streamlit Dashboard UI
Dark-themed, rich financial intelligence dashboard.
"""

from datetime import datetime
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="MarketPulse — AI Financial Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.block-container{padding:1.5rem 2rem;}
.mp-header{background:linear-gradient(135deg,#0f1729,#1a2744,#0d2137);border:1px solid rgba(99,179,237,.2);border-radius:16px;padding:1.8rem 2.5rem;margin-bottom:1.5rem;}
.mp-title{font-size:1.9rem;font-weight:700;color:#e2e8f0;margin:0;}
.mp-sub{color:#718096;font-size:.88rem;margin-top:.2rem;}
.m-card{background:linear-gradient(135deg,#111827,#1a2234);border:1px solid rgba(99,179,237,.15);border-radius:12px;padding:1.1rem 1.4rem;text-align:center;}
.m-lbl{color:#718096;font-size:.72rem;font-weight:500;text-transform:uppercase;letter-spacing:.05em;}
.m-val{color:#e2e8f0;font-size:1.5rem;font-weight:700;margin:.2rem 0;}
.pos{color:#48bb78;}.neg{color:#fc8181;}.neu{color:#a0aec0;}
.badge{display:inline-block;padding:.3rem .9rem;border-radius:20px;font-size:.78rem;font-weight:600;}
.bb{background:rgba(72,187,120,.15);color:#48bb78;border:1px solid rgba(72,187,120,.3);}
.be{background:rgba(252,129,129,.15);color:#fc8181;border:1px solid rgba(252,129,129,.3);}
.bn{background:rgba(160,174,192,.15);color:#a0aec0;border:1px solid rgba(160,174,192,.3);}
.rl-low{background:rgba(72,187,120,.15);color:#48bb78;border:1px solid rgba(72,187,120,.3);}
.rl-medium{background:rgba(246,173,85,.15);color:#f6ad55;border:1px solid rgba(246,173,85,.3);}
.rl-high{background:rgba(252,129,129,.15);color:#fc8181;border:1px solid rgba(252,129,129,.3);}
.rl-critical{background:rgba(245,101,101,.25);color:#f56565;border:1px solid rgba(245,101,101,.5);}
.sh{font-size:.95rem;font-weight:600;color:#90cdf4;letter-spacing:.03em;margin-bottom:.8rem;padding-bottom:.4rem;border-bottom:1px solid rgba(99,179,237,.2);}
.nc{background:rgba(17,24,39,.8);border:1px solid rgba(99,179,237,.1);border-radius:10px;padding:.9rem;margin-bottom:.6rem;}
.nt{color:#e2e8f0;font-size:.88rem;font-weight:500;}
.nm{color:#718096;font-size:.73rem;margin-top:.2rem;}
.rf{background:rgba(252,129,129,.07);border-left:3px solid #fc8181;padding:.55rem .9rem;border-radius:0 8px 8px 0;margin-bottom:.45rem;color:#feb2b2;font-size:.83rem;}
.ii{background:rgba(72,187,120,.05);border-left:3px solid #48bb78;padding:.55rem .9rem;border-radius:0 8px 8px 0;margin-bottom:.45rem;color:#9ae6b4;font-size:.83rem;}
section[data-testid="stSidebar"]{background:#0d1117;border-right:1px solid rgba(99,179,237,.1);}
.stButton>button{background:linear-gradient(135deg,#2b6cb0,#3182ce);color:white;border:none;border-radius:10px;padding:.55rem 2rem;font-weight:600;width:100%;}
</style>
""", unsafe_allow_html=True)


def fmt_cap(cap):
    if not cap: return "N/A"
    if cap >= 1e12: return f"${cap/1e12:.2f}T"
    if cap >= 1e9:  return f"${cap/1e9:.2f}B"
    if cap >= 1e6:  return f"${cap/1e6:.2f}M"
    return f"${cap:,.0f}"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='text-align:center;padding:1rem 0;'><div style='font-size:2rem;'>📈</div><div style='color:#90cdf4;font-weight:700;'>MarketPulse</div><div style='color:#718096;font-size:.75rem;'>AI Financial Intelligence</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🎯 Analysis Settings")
    ticker_input = st.text_input("Stock Ticker", value="AAPL", placeholder="e.g., AAPL, TSLA").strip().upper()
    company_input = st.text_input("Company Name (optional)", placeholder="Auto-resolved if empty").strip()
    depth = st.selectbox("Analysis Depth", ["quick","standard","deep"], index=1,
        format_func=lambda x: {"quick":"⚡ Quick (5d)","standard":"📊 Standard (1mo)","deep":"🔍 Deep (3mo)"}[x])
    st.markdown("---")
    st.markdown("### ⚙️ LLM Settings")
    llm_provider = st.selectbox("LLM Provider", ["openai","google"])
    model_map = {"openai":["gpt-4o-mini","gpt-4o","gpt-3.5-turbo"],"google":["gemini-1.5-flash","gemini-1.5-pro","gemini-2.0-flash"]}
    llm_model = st.selectbox("Model", model_map[llm_provider])
    st.markdown("---")
    run_btn = st.button("🚀 Run Analysis", use_container_width=True)
    st.markdown("<div style='color:#4a5568;font-size:.7rem;text-align:center;'>Powered by LangGraph + LangChain<br>⚡ Multi-Agent AI Pipeline</div>", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='mp-header'><div class='mp-title'>📈 MarketPulse</div><div class='mp-sub'>Autonomous Financial Intelligence Agent — Powered by LangGraph &amp; LangChain</div></div>", unsafe_allow_html=True)

if "result" not in st.session_state:
    st.session_state.result = None

if run_btn:
    if not ticker_input:
        st.error("Please enter a ticker symbol.")
    else:
        os.environ["LLM_PROVIDER"] = llm_provider
        os.environ["LLM_MODEL"] = llm_model
        with st.spinner(f"🤖 Agents analyzing {ticker_input}… (~30-60s)"):
            try:
                from graph.workflow import run_analysis
                st.session_state.result = run_analysis(ticker=ticker_input, company_name=company_input, analysis_depth=depth)
                st.success(f"✅ Analysis complete for {st.session_state.result.get('company_name', ticker_input)}!")
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                st.session_state.result = None

result = st.session_state.result

if result:
    stock   = result.get("stock_summary", {})
    ticker  = result.get("ticker", "")
    cname   = result.get("company_name", ticker)
    sent    = result.get("overall_sentiment", "Neutral")
    risk    = result.get("risk_level", "Medium")
    conf    = result.get("sentiment_confidence", 0.0)
    chg     = stock.get("change_pct", 0)

    sent_cls = {"bullish":"bb","bearish":"be","neutral":"bn"}.get(sent.lower(),"bn")
    risk_cls = f"rl-{risk.lower()}"

    st.markdown(f"<h2 style='color:#e2e8f0;margin:0'>{cname} <span style='color:#718096;font-size:1rem;font-weight:400;'>({ticker})</span></h2><div style='margin-top:.5rem;'><span class='badge {sent_cls}'>📊 {sent}</span> &nbsp; <span class='badge {risk_cls}'>⚠️ {risk} Risk</span></div><br>", unsafe_allow_html=True)

    # Metrics row
    cols = st.columns(6)
    ms = [
        ("💰 Price",    f"${stock.get('current_price',0):.2f}",  f"{chg:+.2f}%"),
        ("🏢 Mkt Cap",  fmt_cap(stock.get("market_cap",0)),      None),
        ("📊 PE Ratio", str(stock.get("pe_ratio","N/A")),         None),
        ("🔄 Beta",     str(stock.get("beta","N/A")),             None),
        ("📈 52W H",    f"${stock.get('52w_high',0):.2f}",       None),
        ("📉 52W L",    f"${stock.get('52w_low',0):.2f}",        None),
    ]
    for col,(lbl,val,ch) in zip(cols,ms):
        with col:
            ch_html = f"<div class='{'pos' if '+' in (ch or '') else 'neg'}'>{ch}</div>" if ch else ""
            st.markdown(f"<div class='m-card'><div class='m-lbl'>{lbl}</div><div class='m-val'>{val}</div>{ch_html}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row
    c1, c2 = st.columns([2,1])
    with c1:
        st.markdown("<div class='sh'>📈 Price History (Candlestick)</div>", unsafe_allow_html=True)
        ph = result.get("price_history",[])
        if ph and "error" not in ph[0]:
            df = pd.DataFrame(ph); df["date"] = pd.to_datetime(df["date"])
            fig = go.Figure(go.Candlestick(x=df["date"],open=df["open"],high=df["high"],low=df["low"],close=df["close"],
                increasing_line_color="#48bb78",decreasing_line_color="#fc8181",name="OHLC"))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(17,24,39,.5)",
                font=dict(color="#a0aec0",size=11),margin=dict(l=0,r=0,t=10,b=0),height=300,
                showlegend=False,xaxis_rangeslider_visible=False,
                xaxis=dict(gridcolor="rgba(99,179,237,.1)"),yaxis=dict(gridcolor="rgba(99,179,237,.1)"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Price history not available.")

    with c2:
        st.markdown("<div class='sh'>🧠 Sentiment Breakdown</div>", unsafe_allow_html=True)
        ss = result.get("sentiment_scores",[])
        if ss:
            cnts = {"Bullish":0,"Bearish":0,"Neutral":0}
            for s in ss: cnts[s.get("sentiment","Neutral")] = cnts.get(s.get("sentiment","Neutral"),0)+1
            fig2 = go.Figure(go.Pie(labels=list(cnts.keys()),values=list(cnts.values()),hole=.6,
                marker=dict(colors=["#48bb78","#fc8181","#a0aec0"]),textinfo="label+percent",
                textfont=dict(color="#e2e8f0",size=11)))
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=0,t=10,b=0),height=300,showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown(f"<div style='text-align:center;padding:3rem 1rem;'><span class='badge {sent_cls}' style='font-size:1.1rem;'>{sent}</span><div style='color:#718096;margin-top:.5rem;font-size:.8rem;'>Confidence: {conf:.0%}</div></div>", unsafe_allow_html=True)

    # Risk + Insights
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("<div class='sh'>⚠️ Risk Flags</div>", unsafe_allow_html=True)
        flags = result.get("risk_flags",[])
        [st.markdown(f"<div class='rf'>🔴 {f}</div>", unsafe_allow_html=True) for f in flags] if flags else st.markdown("<div class='ii'>✅ No significant risk flags identified.</div>", unsafe_allow_html=True)
    with r2:
        st.markdown("<div class='sh'>💡 Key Insights</div>", unsafe_allow_html=True)
        ins = result.get("key_insights",[])
        [st.markdown(f"<div class='ii'>✦ {i}</div>", unsafe_allow_html=True) for i in ins] if ins else st.info("No insights generated.")

    st.markdown("<br>", unsafe_allow_html=True)

    # News + Report
    n1, n2 = st.columns([1,1])
    with n1:
        st.markdown("<div class='sh'>📰 News Feed</div>", unsafe_allow_html=True)
        for art in result.get("raw_news",[])[:6]:
            if "error" in art: continue
            st.markdown(f"<div class='nc'><div class='nt'><a href='{art.get('url','#')}' target='_blank' style='color:#90cdf4;text-decoration:none;'>{art.get('title','N/A')}</a></div><div class='nm'>📰 {art.get('source','Unknown')} · 📅 {art.get('publishedAt','')[:10]}</div></div>", unsafe_allow_html=True)
    with n2:
        st.markdown("<div class='sh'>📄 Investment Report</div>", unsafe_allow_html=True)
        rpt = result.get("final_report","")
        if rpt:
            with st.expander("📋 View Full Report", expanded=True):
                st.markdown(rpt)
            st.download_button("⬇️ Download Report (.md)", data=rpt,
                file_name=f"{ticker}_{datetime.now().strftime('%Y%m%d')}_marketpulse.md", mime="text/markdown")

    with st.expander("🤖 Agent Execution Log"):
        for m in result.get("messages",[]): st.code(m, language=None)

else:
    st.markdown("""
    <div style='text-align:center;padding:4rem 2rem;color:#718096;'>
        <div style='font-size:4rem;'>🤖</div>
        <h3 style='color:#a0aec0;'>Ready to Analyze</h3>
        <p>Enter a stock ticker in the sidebar and click <strong style='color:#90cdf4;'>Run Analysis</strong>.</p>
        <div style='display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;margin-top:2rem;'>
            <div style='background:rgba(17,24,39,.8);border:1px solid rgba(99,179,237,.15);border-radius:12px;padding:1.3rem;width:160px;'>
                <div style='font-size:1.5rem;'>📰</div><div style='color:#e2e8f0;font-weight:600;margin:.4rem 0;'>News Agent</div>
                <div style='font-size:.78rem;'>Fetches financial news</div></div>
            <div style='background:rgba(17,24,39,.8);border:1px solid rgba(99,179,237,.15);border-radius:12px;padding:1.3rem;width:160px;'>
                <div style='font-size:1.5rem;'>🧠</div><div style='color:#e2e8f0;font-weight:600;margin:.4rem 0;'>Sentiment Agent</div>
                <div style='font-size:.78rem;'>LLM sentiment analysis</div></div>
            <div style='background:rgba(17,24,39,.8);border:1px solid rgba(99,179,237,.15);border-radius:12px;padding:1.3rem;width:160px;'>
                <div style='font-size:1.5rem;'>📈</div><div style='color:#e2e8f0;font-weight:600;margin:.4rem 0;'>Stock Agent</div>
                <div style='font-size:.78rem;'>Real-time market data</div></div>
            <div style='background:rgba(17,24,39,.8);border:1px solid rgba(99,179,237,.15);border-radius:12px;padding:1.3rem;width:160px;'>
                <div style='font-size:1.5rem;'>⚠️</div><div style='color:#e2e8f0;font-weight:600;margin:.4rem 0;'>Risk Agent</div>
                <div style='font-size:.78rem;'>Risk flags & insights</div></div>
            <div style='background:rgba(17,24,39,.8);border:1px solid rgba(99,179,237,.15);border-radius:12px;padding:1.3rem;width:160px;'>
                <div style='font-size:1.5rem;'>📄</div><div style='color:#e2e8f0;font-weight:600;margin:.4rem 0;'>Report Agent</div>
                <div style='font-size:.78rem;'>Investment reports</div></div>
        </div>
    </div>""", unsafe_allow_html=True)
