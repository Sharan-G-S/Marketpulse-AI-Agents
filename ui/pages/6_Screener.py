"""
Gainers & Losers Screener — Streamlit Page for MarketPulse.

Scans a broad ticker universe, ranks daily movers, shows breadth metrics,
and lets the user download a full screener report as Markdown.
"""

import streamlit as st

from agents.screener_agent import (
    SCREENER_UNIVERSE,
    run_screener,
    screener_breadth,
)
from tools.screener_helpers import (
    format_breadth_summary,
    format_screener_report,
    format_screener_table,
    mover_emoji,
    screener_entries_to_dicts,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Screener — MarketPulse",
    page_icon="📈",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .screener-header {
        background: linear-gradient(135deg, #1a2e1a 0%, #1e3a2e 100%);
        border: 1px solid #40a060;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .screener-header h2 { color: #a6e3a1; margin: 0; }
    .breadth-card {
        background: #1e1e2e;
        border: 1px solid #333355;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }
    .tab-content { padding-top: 1rem; }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e66f5, #179299);
        color: #fff; border: none; border-radius: 8px; font-weight: 600;
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
    <div class="screener-header">
        <h2>📈 Gainers &amp; Losers Screener</h2>
        <p style="color:#a6adc8;margin:0;">
        Scan the market for today's top movers, worst performers, and most volatile tickers.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([3, 1, 1])
with col_ctrl1:
    extra_raw = st.text_input(
        "Add extra tickers to scan (comma-separated)",
        placeholder="e.g. BABA, TSM, PLTR",
        key="screener_extra",
    )
with col_ctrl2:
    top_n = st.number_input("Top N per group", min_value=3, max_value=20, value=5, step=1)
with col_ctrl3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("🔍 Run Screener", type="primary", use_container_width=True)

extra_tickers = [t.strip().upper() for t in extra_raw.split(",") if t.strip()] if extra_raw else []
universe = list(dict.fromkeys(SCREENER_UNIVERSE + extra_tickers))
st.caption(f"Universe: **{len(universe)}** tickers")

# ---------------------------------------------------------------------------
# Fetch and screen
# ---------------------------------------------------------------------------

if run_btn:
    from tools.indicators import get_all_indicators
    from tools.stock_tools import calculate_price_change, get_price_history, get_stock_summary

    entries = []
    prog = st.progress(0, text="Scanning market…")
    n = len(universe)

    for i, t in enumerate(universe):
        try:
            summary = get_stock_summary.invoke({"ticker": t})
            history = get_price_history.invoke({"ticker": t, "period": "5d", "interval": "1d"})
            metrics = calculate_price_change.invoke({"price_history": history})
            inds    = get_all_indicators(history)

            entries.append({
                "ticker":        t,
                "company_name":  summary.get("company_name", t),
                "sector":        summary.get("sector", "Unknown"),
                "current_price": summary.get("current_price", 0.0),
                "change_pct":    metrics.get("change_pct", 0.0),
                "volume":        summary.get("volume"),
                "market_cap":    summary.get("market_cap"),
                "rsi":           inds.get("rsi"),
            })
        except Exception:
            pass  # silently skip tickers with fetch errors

        prog.progress((i + 1) / n, text=f"Scanned {t} ({i+1}/{n})")

    prog.empty()

    result  = run_screener(entries, top_n=int(top_n))
    breadth = screener_breadth(entries)

    st.session_state["screener_result"]  = result
    st.session_state["screener_breadth"] = breadth
    st.session_state["screener_entries"] = entries

# Load from session
result   = st.session_state.get("screener_result")
breadth  = st.session_state.get("screener_breadth")
entries  = st.session_state.get("screener_entries", [])

if result:
    # -------------------------------------------------------------------
    # Breadth summary row
    # -------------------------------------------------------------------
    adv = breadth.get("advance_count", 0)
    dec = breadth.get("decline_count", 0)
    avg = breadth.get("avg_change_pct", 0.0)
    lbl = breadth.get("breadth_label", "—")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tickers Scanned",  result["total_scanned"])
    m2.metric("Advances / Declines", f"{adv} / {dec}")
    m3.metric("Avg Change", f"{avg:+.2f}%")
    m4.metric("Breadth", lbl)

    st.divider()

    # -------------------------------------------------------------------
    # Tabs: Gainers | Losers | Volatile | All Entries
    # -------------------------------------------------------------------
    tab_g, tab_l, tab_v, tab_all = st.tabs(
        ["🚀 Gainers", "💥 Losers", "⚡ Volatile", "📋 All Entries"]
    )

    import pandas as pd

    with tab_g:
        st.markdown(format_screener_table(result["gainers"], "Top Gainers"))
        df_g = pd.DataFrame(screener_entries_to_dicts(result["gainers"]))
        if not df_g.empty:
            st.dataframe(df_g, use_container_width=True)

    with tab_l:
        st.markdown(format_screener_table(result["losers"], "Top Losers"))
        df_l = pd.DataFrame(screener_entries_to_dicts(result["losers"]))
        if not df_l.empty:
            st.dataframe(df_l, use_container_width=True)

    with tab_v:
        st.markdown(format_screener_table(result["volatile"], "Most Volatile"))
        df_v = pd.DataFrame(screener_entries_to_dicts(result["volatile"]))
        if not df_v.empty:
            st.dataframe(df_v, use_container_width=True)

    with tab_all:
        st.subheader(f"All {len(entries)} Scanned Tickers")
        all_sorted = sorted(entries, key=lambda x: x.get("change_pct", 0), reverse=True)
        df_all = pd.DataFrame(screener_entries_to_dicts(all_sorted))
        if not df_all.empty:
            st.dataframe(df_all, use_container_width=True)

    st.divider()

    # -------------------------------------------------------------------
    # Download full report
    # -------------------------------------------------------------------
    report_md = format_screener_report(result)
    st.download_button(
        label="⬇ Download Screener Report (Markdown)",
        data=report_md,
        file_name="marketpulse_screener_report.md",
        mime="text/markdown",
        key="dl_screener_report",
    )

else:
    st.info("Click **Run Screener** to fetch live data and rank today's movers.")
