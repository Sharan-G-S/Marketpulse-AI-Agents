"""
Risk Dashboard — Streamlit Page for MarketPulse.

Computes and displays portfolio risk metrics (Sharpe, Sortino, Max Drawdown,
VaR, Calmar) for one or more tickers side-by-side.
"""

import pandas as pd
import streamlit as st

from tools.risk_metrics import compute_risk_metrics
from tools.risk_metrics_helpers import (
    format_multi_risk_table,
    format_risk_table,
    risk_label_emoji,
    risk_metrics_to_dict,
    sharpe_badge,
)

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Risk Dashboard — MarketPulse",
    page_icon="⚠️",
    layout="wide",
)

# ── CSS ──────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .risk-header {
        background: linear-gradient(135deg, #2e1e1e 0%, #3a1e1e 100%);
        border: 1px solid #f38ba8;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .risk-header h2 { color: #f38ba8; margin: 0; }
    .metric-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        border: 1px solid #313244;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #f38ba8, #cba6f7);
        color: #1e1e2e; border: none; border-radius: 8px; font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ───────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="risk-header">
        <h2>⚠️ Portfolio Risk Dashboard</h2>
        <p style="color:#a6adc8;margin:0;">
        Quantitative risk metrics: Sharpe, Sortino, Max Drawdown, VaR, and Calmar Ratio.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Controls ─────────────────────────────────────────────────────────────────

c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    raw = st.text_input(
        "Tickers (comma-separated, max 5)",
        value="AAPL, MSFT, TSLA",
        key="risk_tickers",
    )
with c2:
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
with c3:
    rfr = st.number_input(
        "Risk-Free Rate %", min_value=0.0, max_value=15.0, value=5.0, step=0.25
    )
    rfr_dec = rfr / 100

tickers = [t.strip().upper() for t in raw.split(",") if t.strip()][:5]

run_btn = st.button("🔍 Compute Risk Metrics", type="primary")

# ── Fetch + compute ───────────────────────────────────────────────────────────

if run_btn and tickers:
    from tools.stock_tools import get_price_history

    all_metrics = []
    prog = st.progress(0, text="Fetching price history…")

    for i, t in enumerate(tickers):
        try:
            history = get_price_history.invoke({"ticker": t, "period": period, "interval": "1d"})
            m = compute_risk_metrics(history, ticker=t, risk_free_rate=rfr_dec)
            all_metrics.append(m)
        except Exception as e:
            st.warning(f"Could not fetch data for **{t}**: {e}")
        prog.progress((i + 1) / len(tickers), text=f"Computed {t}")

    prog.empty()
    st.session_state["risk_metrics"] = all_metrics

metrics_list = st.session_state.get("risk_metrics", [])

if metrics_list:
    # ── Summary metric tiles ─────────────────────────────────────────────────
    cols = st.columns(len(metrics_list))
    for col, m in zip(cols, metrics_list):
        with col:
            st.metric(
                label=f"**{m['ticker']}** — Risk Level",
                value=risk_label_emoji(m["risk_label"]),
                delta=f"Sharpe {m['sharpe']:.2f}",
            )

    st.divider()

    # ── Comparison table ─────────────────────────────────────────────────────
    if len(metrics_list) > 1:
        st.subheader("📊 Side-by-Side Comparison")
        st.markdown(format_multi_risk_table(metrics_list))
        st.divider()

    # ── Per-ticker drill-down ─────────────────────────────────────────────────
    st.subheader("🔎 Detailed Metrics")
    tabs = st.tabs([m["ticker"] for m in metrics_list])
    for tab, m in zip(tabs, metrics_list):
        with tab:
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Sharpe Ratio",    f"{m['sharpe']:.3f}",
                      delta=sharpe_badge(m["sharpe"]))
            r2.metric("Max Drawdown",    f"{m['max_drawdown']*100:.2f}%")
            r3.metric("Ann. Return",     f"{m['ann_return']*100:+.2f}%")
            r4.metric("Ann. Volatility", f"{m['ann_volatility']*100:.2f}%")
            st.markdown(format_risk_table(m))

    st.divider()

    # ── DataFrame + download ──────────────────────────────────────────────────
    st.subheader("📋 All Metrics Table")
    df = pd.DataFrame([risk_metrics_to_dict(m) for m in metrics_list])
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button(
        "⬇ Download Risk Metrics (CSV)",
        data=csv,
        file_name="marketpulse_risk_metrics.csv",
        mime="text/csv",
        key="dl_risk_csv",
    )

    md_report = "\n\n---\n\n".join(format_risk_table(m) for m in metrics_list)
    st.download_button(
        "⬇ Download Risk Report (Markdown)",
        data=md_report,
        file_name="marketpulse_risk_report.md",
        mime="text/markdown",
        key="dl_risk_md",
    )

else:
    st.info("Enter tickers and click **Compute Risk Metrics** to begin.")
