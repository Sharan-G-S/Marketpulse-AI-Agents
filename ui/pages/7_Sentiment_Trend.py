"""
Sentiment Trend — Streamlit Page for MarketPulse.

Visualises news sentiment scores as a multi-day line chart for any ticker.
Uses real sentiment data from the current session if available, or
synthesises a plausible trend from a single-day snapshot for demo purposes.
"""

import streamlit as st
import pandas as pd

from tools.sentiment_trend import (
    build_sentiment_trend,
    simulate_trend_from_snapshot,
    trend_direction,
    trend_summary_text,
    sentiment_label,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Sentiment Trend — MarketPulse",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .trend-header {
        background: linear-gradient(135deg, #1e1e2e 0%, #2e1e3e 100%);
        border: 1px solid #6c4a9e;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .trend-header h2 { color: #cba6f7; margin: 0; }
    .insight-card {
        background: #1e1e2e;
        border-left: 4px solid #cba6f7;
        border-radius: 0 10px 10px 0;
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="trend-header">
        <h2>📊 News Sentiment Trend</h2>
        <p style="color:#a6adc8;margin:0;">
        Track how news sentiment for a stock evolves over time.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Ticker input + controls
# ---------------------------------------------------------------------------

col_t, col_d, col_b = st.columns([2, 1, 1])
with col_t:
    ticker = st.text_input("Ticker Symbol", value="AAPL", key="trend_ticker").strip().upper()
with col_d:
    sim_days = st.slider("Trend window (days)", min_value=3, max_value=30, value=7)
with col_b:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("📊 Analyse Trend", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Build or load trend
# ---------------------------------------------------------------------------

if run_btn and ticker:
    # Check if session has real sentiment data for this ticker
    session_ticker    = st.session_state.get("ticker", "")
    session_sentiment = st.session_state.get("sentiment_scores", [])

    if session_ticker.upper() == ticker and session_sentiment:
        # Attempt to build a real trend from session data
        trend = build_sentiment_trend(session_sentiment)
        if not trend:
            trend = simulate_trend_from_snapshot(session_sentiment, days=sim_days)
        data_source = "session"
    else:
        # Fetch fresh news + sentiment for the ticker
        try:
            from tools.news_tools import fetch_news
            from agents.sentiment_agent import score_articles

            articles = fetch_news(ticker, max_results=30)
            # Simulate dates spread across the window (articles may lack dates)
            from datetime import datetime, timedelta, timezone as _tz
            today = datetime.now(_tz.utc).date()
            for i, art in enumerate(articles):
                if not art.get("date") and not art.get("publishedAt"):
                    offset = i % sim_days
                    art["date"] = (today - timedelta(days=(sim_days - 1 - offset))).strftime("%Y-%m-%d")

            scored = score_articles(articles)
            trend  = build_sentiment_trend(scored, fallback_date=str(today))
            if not trend:
                trend = simulate_trend_from_snapshot(scored, days=sim_days)
            data_source = "live"
        except Exception:
            # Graceful fallback: synthetic trend with neutral baseline
            dummy = [{"sentiment": "Neutral", "score": 0.0}]
            trend = simulate_trend_from_snapshot(dummy, days=sim_days)
            data_source = "simulated"

    st.session_state["trend_data"]   = trend
    st.session_state["trend_ticker"] = ticker
    st.session_state["trend_source"] = data_source

# Load from session
trend       = st.session_state.get("trend_data", [])
trend_tkr   = st.session_state.get("trend_ticker", ticker)
data_source = st.session_state.get("trend_source", "")

if trend:
    # -------------------------------------------------------------------
    # Source badge
    # -------------------------------------------------------------------
    source_badges = {
        "live":      "🟢 Live news data",
        "session":   "🔵 Current session data",
        "simulated": "🟡 Simulated trend (no live data available)",
    }
    st.caption(source_badges.get(data_source, ""))

    # -------------------------------------------------------------------
    # Summary metrics
    # -------------------------------------------------------------------
    latest   = trend[-1]
    earliest = trend[0]
    direction = trend_direction(trend)
    dir_emoji = {"Improving": "📈", "Deteriorating": "📉", "Stable": "➡️"}.get(direction, "")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ticker",       trend_tkr)
    m2.metric("Latest Score", f"{latest['avg_score']:+.2f}", delta=latest["label"])
    m3.metric("Trend",        f"{direction} {dir_emoji}")
    m4.metric("Days Covered", len(trend))

    st.divider()

    # -------------------------------------------------------------------
    # Line chart
    # -------------------------------------------------------------------
    st.subheader("📈 Sentiment Score Over Time")

    df_trend = pd.DataFrame(trend).set_index("date")
    df_chart  = df_trend[["avg_score"]].rename(columns={"avg_score": "Avg Sentiment Score"})

    st.line_chart(df_chart, use_container_width=True, height=300)

    # -------------------------------------------------------------------
    # Stacked bar (bullish / bearish / neutral counts)
    # -------------------------------------------------------------------
    st.subheader("📰 Article Breakdown by Day")
    df_bar = df_trend[["bullish_count", "bearish_count", "neutral_count"]].rename(
        columns={
            "bullish_count": "Bullish",
            "bearish_count": "Bearish",
            "neutral_count": "Neutral",
        }
    )
    st.bar_chart(df_bar, use_container_width=True, height=220)

    st.divider()

    # -------------------------------------------------------------------
    # Summary narrative
    # -------------------------------------------------------------------
    st.subheader("🗒️ Trend Interpretation")
    st.markdown(
        f'<div class="insight-card">{trend_summary_text(trend_tkr, trend)}</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # -------------------------------------------------------------------
    # Raw data table + download
    # -------------------------------------------------------------------
    with st.expander("📋 Raw Trend Data"):
        st.dataframe(df_trend.reset_index(), use_container_width=True)

    csv_buf = df_trend.reset_index().to_csv(index=False)
    st.download_button(
        label="⬇ Download Trend as CSV",
        data=csv_buf,
        file_name=f"marketpulse_sentiment_trend_{trend_tkr}.csv",
        mime="text/csv",
        key="dl_trend_csv",
    )

else:
    st.info(
        "Enter a ticker and click **Analyse Trend** to visualise news sentiment over time. "
        "If a full analysis has been run from the main page for this ticker, real sentiment "
        "data will be used automatically."
    )
