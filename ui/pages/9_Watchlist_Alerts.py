"""
Watchlist Alerts — Streamlit Page for MarketPulse.
Monitors price, RSI, & volume alerts for watchlist tickers in Claude design system.
"""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS
from tools.watchlist_alerts import evaluate_watchlist, watchlist_alert_summary, SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_INFO

st.set_page_config(page_title="Watchlist Alerts — MarketPulse", page_icon="🔔", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Watchlist Price & Technical Alerts",
    subtitle="Configure custom price movement %, RSI levels, & volume anomaly threshold alerts",
    icon="🔔"
)

st.markdown("<div class='claude-card-title'>📋 Watchlist Configuration</div>", unsafe_allow_html=True)
raw = st.text_input("Tickers to Monitor (comma-separated)", value="AAPL, TSLA, NVDA, AMZN, MSFT", key="wl_tickers")
tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

with st.expander("⚙️ Alert Thresholds Customization", expanded=False):
    tc1, tc2, tc3, tc4 = st.columns(4)
    pct_thresh = tc1.number_input("Price Move % threshold", 1.0, 20.0, 5.0, 0.5)
    rsi_ob = tc2.number_input("RSI Overbought ≥", 50.0, 90.0, 75.0, 1.0)
    rsi_os = tc3.number_input("RSI Oversold ≤", 10.0, 50.0, 25.0, 1.0)
    vol_spike = tc4.number_input("Volume Spike ×", 1.0, 10.0, 2.0, 0.5)

custom_thresholds = {
    "price_change_pct": pct_thresh,
    "rsi_overbought": rsi_ob,
    "rsi_oversold": rsi_os,
    "volume_spike": vol_spike,
}

scan_btn = st.button("🔔 Scan Watchlist for Alerts", use_container_width=True)

if scan_btn and tickers:
    from tools.indicators import get_all_indicators
    from tools.stock_tools import get_price_history, get_stock_summary

    entries = []
    prog = st.progress(0, text="Scanning watchlist assets…")
    for i, t in enumerate(tickers):
        try:
            summary = get_stock_summary.invoke({"ticker": t})
            history = get_price_history.invoke({"ticker": t, "period": "5d", "interval": "1d"})
            inds = get_all_indicators(history)
            entries.append({
                "ticker": t,
                "current_price": summary.get("current_price", 0.0),
                "change_pct": summary.get("change_pct", 0.0),
                "volume": summary.get("volume"),
                "avg_volume": summary.get("averageVolume") or summary.get("avg_volume"),
                "rsi": inds.get("rsi"),
            })
        except Exception:
            pass
        prog.progress((i + 1) / len(tickers), text=f"Scanned {t}")

    prog.empty()
    alerts = evaluate_watchlist(entries, custom_thresholds)
    summary = watchlist_alert_summary(alerts)

    st.session_state["wl_alerts"] = alerts
    st.session_state["wl_entries"] = entries
    st.session_state["wl_summary"] = summary

alerts = st.session_state.get("wl_alerts", [])
summary = st.session_state.get("wl_summary", {})
entries = st.session_state.get("wl_entries", [])

if alerts is not None and summary:
    counts = summary.get("counts", {})
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Alerts", summary.get("total", 0))
    m2.metric("🔴 Critical", counts.get(SEVERITY_CRITICAL, 0))
    m3.metric("🟡 Warnings", counts.get(SEVERITY_WARNING, 0))
    m4.metric("🔵 Info", counts.get(SEVERITY_INFO, 0))

    if alerts:
        st.markdown("<div class='claude-card-title'>🚨 Triggered Alert Feeds</div>", unsafe_allow_html=True)
        for a in alerts:
            st.markdown(f"<div class='claude-flag-risk'>[{a['severity']}] {a['message']}</div>", unsafe_allow_html=True)
    else:
        st.success("✅ No threshold breaches detected across active watchlist.")

    if entries:
        st.markdown("<div class='claude-card-title'>📊 Watchlist Live Snapshot</div>", unsafe_allow_html=True)
        df_entries = pd.DataFrame(entries)
        st.dataframe(df_entries, use_container_width=True, hide_index=True)
else:
    st.info("Click 'Scan Watchlist for Alerts' to evaluate active price and technical triggers.")
