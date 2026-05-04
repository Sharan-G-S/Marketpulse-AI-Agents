"""
Sector Heatmap — Streamlit Page for MarketPulse.

Displays a live sector performance heatmap by scanning the WATCHLIST_DEFAULTS
tickers (plus any user-added ones), computing per-sector heat scores,
and rendering a colour-coded table with momentum indicators.
"""

import streamlit as st

from agents.watchlist_agent import WATCHLIST_DEFAULTS
from tools.heatmap_helpers import (
    format_heatmap_summary,
    format_heatmap_table,
    heatmap_to_dicts,
    heat_score_emoji,
)
from tools.sector_heatmap import build_sector_heatmap

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Sector Heatmap — MarketPulse",
    page_icon="🌡️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .heatmap-header {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a1e3e 100%);
        border: 1px solid #5a3e7a;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .heatmap-header h2 { color: #cba6f7; margin: 0; }
    .metric-tile {
        background: #1e1e2e;
        border: 1px solid #333355;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-tile .value { font-size: 1.8rem; font-weight: 700; color: #cdd6f4; }
    .metric-tile .label { font-size: 0.8rem; color: #6c7086; margin-top: 4px; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="heatmap-header">
        <h2>🌡️ Sector Heatmap</h2>
        <p style="color:#a6adc8;margin:0;">
        Live sector performance heat scores based on price momentum, RSI, and gainer breadth.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Ticker input
# ---------------------------------------------------------------------------

with st.expander("⚙️ Customise Ticker Universe", expanded=False):
    extra_input = st.text_input(
        "Add extra tickers (comma-separated)",
        placeholder="e.g. BABA, TSM, SONY",
        key="heatmap_extra_tickers",
    )

extra_tickers = [t.strip().upper() for t in extra_input.split(",") if t.strip()] if "extra_input" in dir() else []
scan_list = list(dict.fromkeys(WATCHLIST_DEFAULTS + extra_tickers))  # dedup, preserve order

st.caption(f"Scanning **{len(scan_list)}** tickers: {', '.join(scan_list)}")

# ---------------------------------------------------------------------------
# Data fetch (cached per session)
# ---------------------------------------------------------------------------

run_btn = st.button("🔄 Build Heatmap", type="primary", use_container_width=False)

if run_btn or st.session_state.get("heatmap_data"):

    if run_btn:
        # Fetch fresh data
        from tools.stock_tools import calculate_price_change, get_price_history, get_stock_summary
        from tools.indicators import get_all_indicators

        snapshots = []
        progress = st.progress(0, text="Fetching market data…")
        n = len(scan_list)

        for i, t in enumerate(scan_list):
            try:
                summary = get_stock_summary.invoke({"ticker": t})
                history = get_price_history.invoke({"ticker": t, "period": "1mo", "interval": "1d"})
                metrics = calculate_price_change.invoke({"price_history": history})
                indicators = get_all_indicators(history)

                snapshots.append({
                    "ticker": t,
                    "sector": summary.get("sector") or "Unknown",
                    "change_pct": metrics.get("change_pct", 0.0),
                    "rsi": indicators.get("rsi"),
                    "volume": summary.get("volume"),
                })
            except Exception:
                snapshots.append({"ticker": t, "sector": "Unknown", "change_pct": 0.0})

            progress.progress((i + 1) / n, text=f"Fetched {t} ({i+1}/{n})")

        progress.empty()
        heatmap = build_sector_heatmap(snapshots)
        st.session_state["heatmap_data"] = heatmap
        st.session_state["heatmap_snapshots"] = snapshots

    heatmap = st.session_state.get("heatmap_data", [])
    snapshots = st.session_state.get("heatmap_snapshots", [])

    if not heatmap:
        st.warning("No sector data could be built. Please try again.")
        st.stop()

    # -----------------------------------------------------------------------
    # Summary metrics
    # -----------------------------------------------------------------------

    total_tickers = sum(s["ticker_count"] for s in heatmap)
    total_gainers = sum(s["gainers"] for s in heatmap)
    breadth = round(total_gainers / total_tickers * 100, 1) if total_tickers else 0.0
    top_sector = heatmap[0] if heatmap else {}
    bot_sector = heatmap[-1] if heatmap else {}

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Sectors Covered", len(heatmap))
    with c2:
        st.metric("Market Breadth", f"{breadth:.1f}% gainers")
    with c3:
        st.metric(
            "🔥 Hottest Sector",
            top_sector.get("sector", "—"),
            delta=f"{top_sector.get('avg_change_pct', 0):+.2f}%",
        )
    with c4:
        st.metric(
            "🧊 Coolest Sector",
            bot_sector.get("sector", "—"),
            delta=f"{bot_sector.get('avg_change_pct', 0):+.2f}%",
        )

    st.divider()

    # -----------------------------------------------------------------------
    # Heatmap table (as dataframe)
    # -----------------------------------------------------------------------

    st.subheader("📊 Sector Performance Table")

    import pandas as pd

    df = pd.DataFrame(heatmap_to_dicts(heatmap))
    df.index = df.index + 1  # 1-based rank

    # Colour-code heat_score column
    def colour_heat(val: float) -> str:
        if val >= 75:
            return "background-color: #2d4a2d; color: #a6e3a1"
        if val >= 55:
            return "background-color: #2d3f2d; color: #94e2a1"
        if val >= 45:
            return "background-color: #2a2a3e; color: #cdd6f4"
        if val >= 25:
            return "background-color: #4a2d2d; color: #f38ba8"
        return "background-color: #3a1a1a; color: #f38ba8"

    styled = df.style.applymap(colour_heat, subset=["heat_score"])
    st.dataframe(styled, use_container_width=True)

    st.divider()

    # -----------------------------------------------------------------------
    # Summary narrative
    # -----------------------------------------------------------------------

    st.subheader("🗒️ Summary")
    st.markdown(format_heatmap_summary(heatmap))

    st.divider()

    # -----------------------------------------------------------------------
    # Markdown table download
    # -----------------------------------------------------------------------

    md_table = format_heatmap_table(heatmap)
    st.download_button(
        label="⬇ Download Heatmap as Markdown",
        data=md_table,
        file_name="marketpulse_sector_heatmap.md",
        mime="text/markdown",
        key="dl_heatmap_md",
    )

else:
    st.info("Click **Build Heatmap** to fetch live data and compute sector performance scores.")
