"""
News Digest Page — Streamlit UI for MarketPulse.
Fetches & formats deduplicated news digest in Claude design theme.
"""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS
from tools.news_digest import build_digest_entries, deduplicate_articles, digest_sentiment_summary, format_news_digest_markdown, rank_articles

st.set_page_config(page_title="News Digest — MarketPulse", page_icon="📰", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Financial News Digest & Synthesis",
    subtitle="Deduplicated, AI-ranked, and sentiment-scored financial news feed for target assets",
    icon="📰"
)

st.sidebar.markdown("### ⚙️ Digest Settings")
ticker = st.sidebar.text_input("Stock Ticker Symbol", value="AAPL").strip().upper()
max_articles = st.sidebar.slider("Max Digest Articles", 3, 20, 10)
fetch_btn = st.sidebar.button("📰 Fetch News Digest", use_container_width=True)

if fetch_btn or "digest_entries" in st.session_state:
    if fetch_btn and ticker:
        with st.spinner(f"Scraping & deduplicating news articles for {ticker}..."):
            try:
                from agents.sentiment_agent import score_articles
                from tools.news_tools import fetch_news

                raw_articles = fetch_news(ticker, max_results=30)
                scored = score_articles(raw_articles)
                deduped = deduplicate_articles(scored, threshold=0.55)
                ranked = rank_articles(deduped, top_n=max_articles)
                entries = build_digest_entries(ranked)
                stats = digest_sentiment_summary(entries)
                md_digest = format_news_digest_markdown(ticker, entries, max_articles)

                st.session_state["digest_entries"] = entries
                st.session_state["digest_stats"] = stats
                st.session_state["digest_md"] = md_digest
            except Exception as e:
                st.error(f"Failed to fetch news digest: {e}")

    entries = st.session_state.get("digest_entries", [])
    stats = st.session_state.get("digest_stats", {})
    md = st.session_state.get("digest_md", "")

    if entries:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Articles", stats.get("total", 0))
        m2.metric("🟢 Bullish", stats.get("bullish_count", 0))
        m3.metric("🔴 Bearish", stats.get("bearish_count", 0))
        m4.metric("Avg Score", f"{stats.get('avg_score', 0):+.2f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='claude-card-title'>📰 Ranked Digest Articles</div>", unsafe_allow_html=True)
        for i, e in enumerate(entries, 1):
            st.markdown(
                f"""
                <div class='claude-news-item'>
                    <div style='font-weight:600;font-size:0.92rem;'>
                        <a href='{e.get("url", "#")}' target='_blank' style='color:{CLAUDE_COLORS["terracotta"]};text-decoration:none;'>
                            {i}. {e["title"]}
                        </a>
                    </div>
                    <div style='color:{CLAUDE_COLORS["text_secondary"]};font-size:0.78rem;margin-top:0.3rem;'>
                        Score: <strong>{e["score"]:+.2f} ({e["sentiment"]})</strong> · Source: {e["source"]} · Date: {e["date"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.download_button(
            "⬇ Download Digest Markdown (.md)",
            data=md,
            file_name=f"marketpulse_digest_{ticker}.md",
            mime="text/markdown",
            key="dl_digest_md",
        )
else:
    st.info("Enter a ticker symbol and click 'Fetch News Digest' in the sidebar.")
