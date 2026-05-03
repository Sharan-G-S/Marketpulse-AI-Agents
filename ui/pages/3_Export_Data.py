"""
MarketPulse — CSV Data Export Page

Provides a Streamlit UI for downloading portfolio positions, watchlist data,
and triggered alerts as CSV files. Works entirely with data already cached in
Streamlit's session state by the main dashboard.
"""

import streamlit as st

from tools.csv_export import export_alerts_csv, export_portfolio_csv, export_watchlist_csv

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Export Data — MarketPulse",
    page_icon="📥",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .export-card {
        background: #1e1e2e;
        border: 1px solid #333355;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .export-card h3 { color: #a6e3a1; margin-bottom: 0.25rem; }
    .export-card p  { color: #cdd6f4; font-size: 0.9rem; }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e66f5, #8839ef);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.4rem;
        font-weight: 600;
        transition: opacity 0.2s;
    }
    .stDownloadButton > button:hover { opacity: 0.85; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("📥 Export Data")
st.markdown(
    "Download your portfolio positions, watchlist snapshot, and active alerts as CSV files "
    "for use in spreadsheets or further analysis."
)
st.divider()

# ---------------------------------------------------------------------------
# Helper — retrieve session state values safely
# ---------------------------------------------------------------------------


def _get(key: str, default=None):
    return st.session_state.get(key, default)


# ---------------------------------------------------------------------------
# Portfolio CSV export
# ---------------------------------------------------------------------------

st.markdown("### 📊 Portfolio Positions")

portfolio_result = _get("portfolio_result")
positions = (portfolio_result or {}).get("positions", [])

if positions:
    valid = [p for p in positions if p.get("market_value") is not None]
    st.success(f"{len(valid)} position(s) available for export.")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"**Total market value:** ${(portfolio_result or {}).get('total_market_value', 0):,.2f}  \n"
            f"**Unrealised P&L:** ${(portfolio_result or {}).get('total_unrealised_pnl', 0):,.2f}  \n"
            f"**Diversification:** {(portfolio_result or {}).get('diversification_label', '—')}"
        )
    with col2:
        csv_data = export_portfolio_csv(valid)
        st.download_button(
            label="⬇ Download Portfolio CSV",
            data=csv_data,
            file_name="marketpulse_portfolio.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_portfolio",
        )
else:
    st.info(
        "No portfolio data found in session. Run a portfolio analysis from the main "
        "dashboard first, then return here to export."
    )

st.divider()

# ---------------------------------------------------------------------------
# Watchlist CSV export
# ---------------------------------------------------------------------------

st.markdown("### 📋 Watchlist Snapshot")

stock_summary = _get("stock_summary", {})
watchlist = stock_summary.get("watchlist", []) if isinstance(stock_summary, dict) else []

if watchlist:
    valid_wl = [w for w in watchlist if "error" not in w]
    st.success(f"{len(valid_wl)} ticker(s) in the current watchlist snapshot.")

    col1, col2 = st.columns([3, 1])
    with col1:
        if valid_wl:
            tickers_str = ", ".join(w.get("ticker", "?") for w in valid_wl)
            st.markdown(f"**Tickers:** {tickers_str}")
    with col2:
        csv_data = export_watchlist_csv(valid_wl)
        st.download_button(
            label="⬇ Download Watchlist CSV",
            data=csv_data,
            file_name="marketpulse_watchlist.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_watchlist",
        )
else:
    st.info(
        "No watchlist data found in session. Run an analysis from the main dashboard "
        "to populate the watchlist, then return here to export."
    )

st.divider()

# ---------------------------------------------------------------------------
# Alerts CSV export
# ---------------------------------------------------------------------------

st.markdown("### 🚨 Triggered Alerts")

alerts = stock_summary.get("alerts", []) if isinstance(stock_summary, dict) else []

if alerts:
    n_critical = sum(1 for a in alerts if a.get("severity") == "critical")
    n_warning = sum(1 for a in alerts if a.get("severity") == "warning")
    n_info = sum(1 for a in alerts if a.get("severity") == "info")

    st.warning(
        f"**{len(alerts)} alert(s) triggered** — "
        f"{n_critical} critical · {n_warning} warning · {n_info} info"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        # Show the alert digest if available
        digest = stock_summary.get("alert_digest", "")
        if digest:
            with st.expander("View alert digest", expanded=False):
                st.markdown(digest)
    with col2:
        csv_data = export_alerts_csv(alerts)
        st.download_button(
            label="⬇ Download Alerts CSV",
            data=csv_data,
            file_name="marketpulse_alerts.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_alerts",
        )
else:
    st.info(
        "No alerts in current session. Alerts are generated automatically during "
        "a watchlist scan on the main dashboard."
    )

st.divider()

# ---------------------------------------------------------------------------
# Footer note
# ---------------------------------------------------------------------------

st.caption(
    "CSV files are generated from the current session data and reflect a point-in-time "
    "snapshot. Re-run an analysis on the main dashboard to refresh the data before exporting."
)
