"""
Watchlist Alerts — Streamlit Page for MarketPulse.

Lets users build a watchlist, set custom thresholds, and scan for
price/RSI/volume alerts in real time.
"""

import pandas as pd
import streamlit as st

from tools.watchlist_alerts import (
    DEFAULT_WATCHLIST_THRESHOLDS,
    SEVERITY_CRITICAL,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    evaluate_watchlist,
    watchlist_alert_summary,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Watchlist Alerts — MarketPulse",
    page_icon="🔔",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .alert-header {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
        border: 1px solid #f9e2af;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .alert-header h2 { color: #f9e2af; margin: 0; }
    .alert-critical { border-left: 4px solid #f38ba8; padding: 0.6rem 1rem;
                      background: #2e1e2e; border-radius: 0 8px 8px 0; margin: 4px 0; }
    .alert-warning  { border-left: 4px solid #f9e2af; padding: 0.6rem 1rem;
                      background: #2e2a1e; border-radius: 0 8px 8px 0; margin: 4px 0; }
    .alert-info     { border-left: 4px solid #89b4fa; padding: 0.6rem 1rem;
                      background: #1e2a3e; border-radius: 0 8px 8px 0; margin: 4px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="alert-header">
        <h2>🔔 Watchlist Price Alerts</h2>
        <p style="color:#a6adc8;margin:0;">
        Monitor your watchlist tickers against custom price, RSI, and volume thresholds.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Watchlist input ───────────────────────────────────────────────────────────

st.subheader("📋 Your Watchlist")
raw = st.text_input(
    "Tickers to monitor (comma-separated)",
    value="AAPL, TSLA, NVDA, AMZN, MSFT",
    key="wl_tickers",
)
tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

# ── Threshold controls ────────────────────────────────────────────────────────

with st.expander("⚙️ Alert Thresholds (click to customise)", expanded=False):
    tc1, tc2, tc3, tc4 = st.columns(4)
    pct_thresh  = tc1.number_input("Price Move % threshold", 1.0, 20.0, 5.0, 0.5)
    rsi_ob      = tc2.number_input("RSI Overbought ≥",       50.0, 90.0, 75.0, 1.0)
    rsi_os      = tc3.number_input("RSI Oversold ≤",         10.0, 50.0, 25.0, 1.0)
    vol_spike   = tc4.number_input("Volume Spike ×",          1.0, 10.0,  2.0, 0.5)

custom_thresholds = {
    "price_change_pct": pct_thresh,
    "rsi_overbought":   rsi_ob,
    "rsi_oversold":     rsi_os,
    "volume_spike":     vol_spike,
}

# ── Run scan button ───────────────────────────────────────────────────────────

scan_btn = st.button("🔍 Scan Watchlist", type="primary")

if scan_btn and tickers:
    from tools.indicators import get_all_indicators
    from tools.stock_tools import get_price_history, get_stock_summary

    entries = []
    prog = st.progress(0, text="Scanning watchlist…")

    for i, t in enumerate(tickers):
        try:
            summary = get_stock_summary.invoke({"ticker": t})
            history = get_price_history.invoke({"ticker": t, "period": "5d", "interval": "1d"})
            inds    = get_all_indicators(history)

            entries.append({
                "ticker":        t,
                "current_price": summary.get("current_price", 0.0),
                "change_pct":    summary.get("change_pct", 0.0),
                "volume":        summary.get("volume"),
                "avg_volume":    summary.get("averageVolume") or summary.get("avg_volume"),
                "rsi":           inds.get("rsi"),
            })
        except Exception:
            pass
        prog.progress((i + 1) / len(tickers), text=f"Scanned {t}")

    prog.empty()
    alerts = evaluate_watchlist(entries, custom_thresholds)
    summary = watchlist_alert_summary(alerts)

    st.session_state["wl_alerts"]  = alerts
    st.session_state["wl_entries"] = entries
    st.session_state["wl_summary"] = summary

# ── Display results ───────────────────────────────────────────────────────────

alerts  = st.session_state.get("wl_alerts", [])
summary = st.session_state.get("wl_summary", {})
entries = st.session_state.get("wl_entries", [])

if alerts is not None and st.session_state.get("wl_summary"):
    # Status bar
    st.info(summary.get("status", ""))

    counts = summary.get("counts", {})
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Alerts",  summary.get("total", 0))
    m2.metric("🔴 Critical",    counts.get(SEVERITY_CRITICAL, 0))
    m3.metric("🟡 Warnings",    counts.get(SEVERITY_WARNING, 0))
    m4.metric("🔵 Info",        counts.get(SEVERITY_INFO, 0))

    st.divider()

    if alerts:
        st.subheader("🚨 Active Alerts")
        css_class = {
            SEVERITY_CRITICAL: "alert-critical",
            SEVERITY_WARNING:  "alert-warning",
            SEVERITY_INFO:     "alert-info",
        }
        for a in alerts:
            cls = css_class.get(a["severity"], "alert-info")
            st.markdown(
                f'<div class="{cls}"><b>[{a["severity"]}]</b> {a["message"]}</div>',
                unsafe_allow_html=True,
            )

        st.divider()
        st.subheader("📊 Alert Table")
        df_alerts = pd.DataFrame([
            {
                "Ticker":    a["ticker"],
                "Type":      a["alert_type"],
                "Severity":  a["severity"],
                "Message":   a["message"],
                "Value":     a["value"],
                "Threshold": a["threshold"],
            }
            for a in alerts
        ])
        st.dataframe(df_alerts, use_container_width=True)

        csv = df_alerts.to_csv(index=False)
        st.download_button(
            "⬇ Download Alerts (CSV)",
            data=csv,
            file_name="marketpulse_watchlist_alerts.csv",
            mime="text/csv",
            key="dl_wl_alerts",
        )
    else:
        st.success("✅ No alerts triggered — all tickers within defined thresholds.")

    if entries:
        st.divider()
        st.subheader("📋 Watchlist Snapshot")
        df_entries = pd.DataFrame([
            {
                "Ticker":  e.get("ticker"),
                "Price":   e.get("current_price"),
                "Change%": e.get("change_pct"),
                "RSI":     e.get("rsi"),
                "Volume":  e.get("volume"),
            }
            for e in entries
        ])
        st.dataframe(df_entries, use_container_width=True)

else:
    st.info("Enter tickers and click **Scan Watchlist** to check for active alerts.")
