"""
Compare Stocks — Streamlit Page for MarketPulse.

Lets the user enter 2–5 ticker symbols, fetches live data for each,
runs the ComparisonAgent to score them, and renders a side-by-side
fundamentals table, score breakdown, and ranked recommendations.
"""

import streamlit as st

from agents.comparison_agent import compare_tickers, score_label
from agents.comparison_helpers import (
    format_comparison_table,
    format_rankings_summary,
    format_score_breakdown_table,
    score_emoji,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Compare Stocks — MarketPulse",
    page_icon="⚖️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .compare-header {
        background: linear-gradient(135deg, #1e2e1e 0%, #1e2d3e 100%);
        border: 1px solid #3e7a5a;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .compare-header h2 { color: #a6e3a1; margin: 0; }
    .winner-box {
        background: linear-gradient(135deg, #1e3e2e, #1a2d1a);
        border: 2px solid #a6e3a1;
        border-radius: 12px;
        padding: 1.2rem 2rem;
        margin: 1rem 0;
        text-align: center;
    }
    .winner-box h3 { color: #a6e3a1; margin: 0; font-size: 1.4rem; }
    .winner-box p  { color: #cdd6f4; margin: 4px 0 0; }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e66f5, #8839ef);
        color: #fff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
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
    <div class="compare-header">
        <h2>⚖️ Compare Stocks</h2>
        <p style="color:#a6adc8;margin:0;">
        Side-by-side fundamentals, technicals, and composite scoring across 2–5 tickers.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Ticker input
# ---------------------------------------------------------------------------

col_input, col_btn = st.columns([4, 1])
with col_input:
    raw_input = st.text_input(
        "Enter 2–5 ticker symbols (comma-separated)",
        value="AAPL, MSFT, GOOGL",
        placeholder="e.g. AAPL, TSLA, NVDA",
        key="compare_tickers_input",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("⚖️ Compare", type="primary", use_container_width=True)

tickers_to_compare = [t.strip().upper() for t in raw_input.split(",") if t.strip()]

# Validate count
if len(tickers_to_compare) < 2:
    st.warning("Please enter at least 2 ticker symbols.")
elif len(tickers_to_compare) > 5:
    st.warning("Maximum 5 tickers allowed. Only the first 5 will be used.")
    tickers_to_compare = tickers_to_compare[:5]

# ---------------------------------------------------------------------------
# Fetch + compare
# ---------------------------------------------------------------------------

if run_btn and 2 <= len(tickers_to_compare) <= 5:
    from tools.stock_tools import calculate_price_change, get_price_history, get_stock_summary
    from tools.indicators import get_all_indicators, compute_macd

    tickers_data = []
    progress = st.progress(0, text="Fetching data…")
    n = len(tickers_to_compare)

    for i, t in enumerate(tickers_to_compare):
        try:
            summary   = get_stock_summary.invoke({"ticker": t})
            history   = get_price_history.invoke({"ticker": t, "period": "1mo", "interval": "1d"})
            metrics   = calculate_price_change.invoke({"price_history": history})
            indics    = get_all_indicators(history)
            closes    = [r["close"] for r in history if "close" in r]
            macd_data = indics.get("macd") or {}
            mas       = indics.get("moving_averages") or {}

            tickers_data.append({
                "ticker":        t,
                "company_name":  summary.get("company_name", t),
                "current_price": summary.get("current_price"),
                "change_pct":    metrics.get("change_pct", 0.0),
                "market_cap":    summary.get("market_cap"),
                "pe_ratio":      summary.get("pe_ratio"),
                "beta":          summary.get("beta"),
                "52w_high":      summary.get("52w_high"),
                "52w_low":       summary.get("52w_low"),
                "sector":        summary.get("sector"),
                "rsi":           indics.get("rsi"),
                "macd":          macd_data,
                "sma_20":        mas.get("sma_20"),
                "sma_50":        mas.get("sma_50"),
                "ma_signal":     mas.get("ma_signal"),
            })
        except Exception as e:
            st.warning(f"Could not fetch data for **{t}**: {e}")

        progress.progress((i + 1) / n, text=f"Fetched {t} ({i+1}/{n})")

    progress.empty()

    if len(tickers_data) < 2:
        st.error("Could not fetch data for enough tickers. Please check your inputs.")
        st.stop()

    result = compare_tickers(tickers_data)
    st.session_state["comparison_result"] = result

# Load from session if already computed
result = st.session_state.get("comparison_result")

if result and not result.get("error"):
    tickers = result.get("tickers", [])
    breakdown = result.get("breakdown", {})
    winner = result.get("winner")

    # -------------------------------------------------------------------
    # Winner banner
    # -------------------------------------------------------------------
    winner_score = breakdown.get(winner, {}).get("composite", 0)
    winner_label = breakdown.get(winner, {}).get("label", "")
    st.markdown(
        f"""
        <div class="winner-box">
            <h3>🏅 Top Pick: {winner} — {winner_score:.1f} / 100</h3>
            <p>{score_emoji(winner_score)} {winner_label} based on composite scoring</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------
    # Score metric tiles
    # -------------------------------------------------------------------
    cols = st.columns(len(tickers))
    for col, t in zip(cols, tickers):
        s = breakdown.get(t, {}).get("composite", 0)
        lbl = breakdown.get(t, {}).get("label", "")
        col.metric(
            label=f"{score_emoji(s)} {t}",
            value=f"{s:.1f} / 100",
            delta=lbl,
        )

    st.divider()

    # -------------------------------------------------------------------
    # Fundamentals comparison table
    # -------------------------------------------------------------------
    st.subheader("📋 Fundamentals & Technicals")
    st.markdown(format_comparison_table(result))

    st.divider()

    # -------------------------------------------------------------------
    # Score breakdown table
    # -------------------------------------------------------------------
    st.subheader("📐 Score Component Breakdown")
    st.markdown(format_score_breakdown_table(result))

    st.divider()

    # -------------------------------------------------------------------
    # Rankings
    # -------------------------------------------------------------------
    st.subheader("🏆 Rankings")
    st.markdown(format_rankings_summary(result))

    st.divider()

    # -------------------------------------------------------------------
    # Download buttons
    # -------------------------------------------------------------------
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="⬇ Download Comparison Table (Markdown)",
            data=format_comparison_table(result),
            file_name=f"marketpulse_comparison_{'_vs_'.join(tickers)}.md",
            mime="text/markdown",
            key="dl_compare_md",
        )
    with c2:
        st.download_button(
            label="⬇ Download Rankings Summary (Markdown)",
            data=format_rankings_summary(result),
            file_name=f"marketpulse_rankings_{'_vs_'.join(tickers)}.md",
            mime="text/markdown",
            key="dl_rankings_md",
        )

elif not result:
    st.info("Enter 2–5 tickers above and click **Compare** to start the analysis.")
