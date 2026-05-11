"""
News Digest Page — Streamlit UI for MarketPulse.

Fetches and formats a deduplicated, ranked news digest for any ticker
with aggregate sentiment stats and a Markdown download.
"""

import pandas as pd
import streamlit as st

from tools.news_digest import (
    build_digest_entries,
    deduplicate_articles,
    digest_sentiment_summary,
    format_news_digest_markdown,
    rank_articles,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="News Digest — MarketPulse",
    page_icon="📰",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .digest-header {
        background: linear-gradient(135deg, #2a1e2e 0%, #3a2e1e 100%);
        border: 1px solid #cba6f7;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .digest-header h2 { color: #cba6f7; margin: 0; }
    .art-card {
        background: #1e1e2e;
        border-left: 4px solid #cba6f7;
        border-radius: 0 10px 10px 0;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .bull { color: #a6e3a1; }
    .bear { color: #f38ba8; }
    .neut { color: #a6adc8; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="digest-header">
        <h2>📰 News Digest</h2>
        <p style="color:#a6adc8;margin:0;">
        Deduplicated, sentiment-ranked news articles for any ticker.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Controls ──────────────────────────────────────────────────────────────────

c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    ticker = st.text_input("Ticker Symbol", value="AAPL", key="digest_ticker").strip().upper()
with c2:
    max_articles = st.slider("Max articles", 3, 20, 10)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("📰 Fetch Digest", type="primary", use_container_width=True)

# ── Fetch + process ───────────────────────────────────────────────────────────

if run_btn and ticker:
    try:
        from agents.sentiment_agent import score_articles
        from tools.news_tools import fetch_news

        raw_articles = fetch_news(ticker, max_results=30)
        scored       = score_articles(raw_articles)
        deduped      = deduplicate_articles(scored, threshold=0.55)
        ranked       = rank_articles(deduped, top_n=max_articles)
        entries      = build_digest_entries(ranked)
        stats        = digest_sentiment_summary(entries)
        md_digest    = format_news_digest_markdown(ticker, entries, max_articles)

        st.session_state["digest_entries"] = entries
        st.session_state["digest_stats"]   = stats
        st.session_state["digest_md"]      = md_digest
        st.session_state["digest_ticker"]  = ticker

    except Exception as e:
        st.error(f"Could not fetch news: {e}")

entries  = st.session_state.get("digest_entries", [])
stats    = st.session_state.get("digest_stats", {})
md       = st.session_state.get("digest_md", "")
d_ticker = st.session_state.get("digest_ticker", ticker)

if entries:
    # ── Sentiment summary metrics ─────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Articles", stats.get("total", 0))
    m2.metric("🟢 Bullish",     stats.get("bullish_count", 0))
    m3.metric("🔴 Bearish",     stats.get("bearish_count", 0))
    m4.metric("Avg Score",      f"{stats.get('avg_score', 0):+.2f}")

    dominant = stats.get("dominant_sentiment", "Neutral")
    st.caption(f"**Dominant sentiment:** {dominant}")

    st.divider()

    # ── Article cards ─────────────────────────────────────────────────────────
    st.subheader(f"📋 Top {len(entries)} Articles — {d_ticker}")

    _EMOJI = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "⚪"}
    _CSS   = {"Bullish": "bull", "Bearish": "bear", "Neutral": "neut"}

    for i, e in enumerate(entries, 1):
        emoji = _EMOJI.get(e["sentiment"], "⚪")
        css   = _CSS.get(e["sentiment"], "neut")
        url   = e.get("url", "")
        title_html = f'<a href="{url}" target="_blank">{e["title"]}</a>' if url else e["title"]

        st.markdown(
            f"""
            <div class="art-card">
                <b>{i}. {emoji} {title_html}</b><br>
                <span class="{css}">{e["sentiment"]} ({e["score"]:+.2f})</span>
                &nbsp;·&nbsp; {e["source"]} &nbsp;·&nbsp; {e["date"]}<br>
                <small>{e["snippet"]}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Raw table + Markdown download ─────────────────────────────────────────
    with st.expander("📊 Raw Data Table"):
        df = pd.DataFrame(entries)
        st.dataframe(df[["title", "source", "date", "sentiment", "score"]], use_container_width=True)

    st.download_button(
        "⬇ Download Digest (Markdown)",
        data=md,
        file_name=f"marketpulse_digest_{d_ticker}.md",
        mime="text/markdown",
        key="dl_digest_md",
    )

else:
    st.info("Enter a ticker and click **Fetch Digest** to get the latest news.")
