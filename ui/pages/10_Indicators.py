"""
Technical Indicator Dashboard — Streamlit Page for MarketPulse.

Shows RSI, MACD, Moving Average crossover, and Bollinger Band signals
for up to 5 tickers side-by-side.
"""

import pandas as pd
import streamlit as st

from tools.indicator_signals import (
    bollinger_signal,
    format_indicator_table,
    format_multi_indicator_table,
    ma_signal,
    macd_signal,
    overall_signal,
    rsi_signal,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Indicators — MarketPulse",
    page_icon="📉",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .ind-header {
        background: linear-gradient(135deg, #1e2a1e 0%, #1e3a2e 100%);
        border: 1px solid #a6e3a1;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .ind-header h2 { color: #a6e3a1; margin: 0; }
    .signal-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        border: 1px solid #313244;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="ind-header">
        <h2>📉 Technical Indicator Dashboard</h2>
        <p style="color:#a6adc8;margin:0;">
        RSI, MACD, Moving Average crossovers, and Bollinger Bands for any ticker.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Controls ──────────────────────────────────────────────────────────────────

c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    raw = st.text_input(
        "Tickers (comma-separated, max 5)",
        value="AAPL, MSFT, NVDA",
        key="ind_tickers",
    )
with c2:
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=1, key="ind_period")
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("📉 Fetch Indicators", type="primary", use_container_width=True)

tickers = [t.strip().upper() for t in raw.split(",") if t.strip()][:5]

# ── Fetch & compute ───────────────────────────────────────────────────────────

if run_btn and tickers:
    from tools.indicators import get_all_indicators
    from tools.stock_tools import get_price_history, get_stock_summary

    entries = []
    prog = st.progress(0, text="Fetching indicators…")

    for i, t in enumerate(tickers):
        try:
            summary = get_stock_summary.invoke({"ticker": t})
            history = get_price_history.invoke({"ticker": t, "period": period, "interval": "1d"})
            inds    = get_all_indicators(history)

            entries.append({
                "ticker":        t,
                "current_price": summary.get("current_price", 0.0),
                "change_pct":    summary.get("change_pct", 0.0),
                "rsi":           inds.get("rsi"),
                "macd":          inds.get("macd"),
                "ma_signal":     inds.get("ma_signal"),
                "bb":            inds.get("bollinger_bands"),
            })
        except Exception as e:
            st.warning(f"Could not fetch **{t}**: {e}")
        prog.progress((i + 1) / len(tickers), text=f"Fetched {t}")

    prog.empty()
    st.session_state["ind_entries"] = entries

entries = st.session_state.get("ind_entries", [])

if entries:
    # ── Overall signal tiles ──────────────────────────────────────────────────
    st.subheader("🎯 Overall Signals")
    sig_cols = st.columns(len(entries))
    for col, e in zip(sig_cols, entries):
        sig = overall_signal(e.get("rsi"), e.get("macd"), e.get("ma_signal"))
        col.metric(
            label=e["ticker"],
            value=sig,
            delta=f"RSI {e['rsi']:.1f}" if e.get("rsi") else "RSI N/A",
        )

    st.divider()

    # ── Comparison table ──────────────────────────────────────────────────────
    if len(entries) > 1:
        st.subheader("📊 Indicator Comparison")
        st.markdown(format_multi_indicator_table(entries))
        st.divider()

    # ── Per-ticker detailed view ──────────────────────────────────────────────
    st.subheader("🔎 Detailed Breakdown")
    tabs = st.tabs([e["ticker"] for e in entries])

    for tab, e in zip(tabs, entries):
        with tab:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("RSI",      f"{e['rsi']:.1f}" if e.get("rsi") else "N/A",
                      delta=rsi_signal(e.get("rsi")))
            c2.metric("MACD",     macd_signal(e.get("macd")))
            c3.metric("MA Cross", ma_signal(e.get("ma_signal")))
            c4.metric("Price",    f"${e.get('current_price', 0):.2f}",
                      delta=f"{e.get('change_pct', 0):+.2f}%")

            st.markdown(
                format_indicator_table(
                    e["ticker"],
                    e.get("current_price", 0),
                    e.get("rsi"),
                    e.get("macd"),
                    e.get("ma_signal"),
                    e.get("bb"),
                )
            )

    st.divider()

    # ── DataFrame ─────────────────────────────────────────────────────────────
    st.subheader("📋 Raw Data Table")
    df = pd.DataFrame([
        {
            "Ticker":    e.get("ticker"),
            "Price":     e.get("current_price"),
            "Change%":   e.get("change_pct"),
            "RSI":       e.get("rsi"),
            "RSI Signal": rsi_signal(e.get("rsi")),
            "MACD":      macd_signal(e.get("macd")),
            "MA Signal": ma_signal(e.get("ma_signal")),
            "Overall":   overall_signal(e.get("rsi"), e.get("macd"), e.get("ma_signal")),
        }
        for e in entries
    ])
    st.dataframe(df, use_container_width=True)

else:
    st.info("Enter tickers and click **Fetch Indicators** to view technical signals.")
