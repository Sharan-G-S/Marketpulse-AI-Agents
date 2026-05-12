"""Earnings Surprise Tracker — Streamlit page for MarketPulse."""

import pandas as pd
import streamlit as st

from tools.earnings_surprise import (
    compute_earnings_history,
    earnings_trend,
    format_earnings_table,
)

st.set_page_config(page_title="Earnings Surprise — MarketPulse", page_icon="📊", layout="wide")

st.markdown("""
<style>
.earn-header { background: linear-gradient(135deg,#1e1e2e,#2e1e2e);
  border:1px solid #f38ba8; border-radius:14px; padding:1.5rem 2rem; margin-bottom:1.5rem; }
.earn-header h2 { color:#f38ba8; margin:0; }
.beat { color:#a6e3a1; font-weight:700; }
.miss { color:#f38ba8; font-weight:700; }
</style>""", unsafe_allow_html=True)

st.markdown(
    '<div class="earn-header"><h2>📊 Earnings Surprise Tracker</h2>'
    '<p style="color:#a6adc8;margin:0;">Compare reported EPS against estimates and track beat/miss history.</p></div>',
    unsafe_allow_html=True,
)

st.subheader("📋 Enter Earnings Records")
st.caption("Format: **TICKER, period, reported_eps, estimated_eps** (one per line).  "
           "Example: `AAPL, Q1 2026, 2.20, 2.00`")

default_data = (
    "AAPL, Q1 2026, 2.20, 2.00\n"
    "AAPL, Q4 2025, 2.10, 2.15\n"
    "AAPL, Q3 2025, 1.96, 1.80\n"
    "MSFT, Q1 2026, 3.45, 3.10\n"
    "TSLA, Q1 2026, 0.45, 0.55\n"
)

raw = st.text_area("Records", value=default_data, height=160, key="earn_records")
run_btn = st.button("📈 Compute Surprises", type="primary")

records, parse_errors = [], []
for line in raw.strip().splitlines():
    line = line.strip()
    if not line:
        continue
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 4:
        parse_errors.append(f"⚠️ Skipped: `{line}`")
        continue
    try:
        records.append({
            "ticker":       parts[0].upper(),
            "period":       parts[1],
            "reported_eps": float(parts[2]),
            "estimated_eps":float(parts[3]),
        })
    except ValueError:
        parse_errors.append(f"⚠️ Non-numeric EPS in: `{line}`")

for e in parse_errors:
    st.warning(e)

if run_btn and records:
    results = compute_earnings_history(records)
    st.session_state["earn_results"] = results

results = st.session_state.get("earn_results", [])

if results:
    # Summary table
    st.subheader("📋 Surprise Results")
    rows = [{
        "Ticker":       r["ticker"],
        "Period":       r["period"],
        "Reported EPS": f"${r['reported_eps']:.2f}",
        "Est. EPS":     f"${r['estimated_eps']:.2f}",
        "Surprise %":   f"{r['eps_surprise_pct']:+.2f}%",
        "Verdict":      r["eps_verdict"],
        "Overall":      r["overall_verdict"],
    } for r in results]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    # Per-ticker trend
    tickers = list({r["ticker"] for r in results})
    st.divider()
    st.subheader("📈 Earnings Trend by Ticker")
    for t in tickers:
        t_results = [r for r in results if r["ticker"] == t]
        trend = earnings_trend(t_results)
        st.markdown(f"**{t}** — {trend['trend_label']} &nbsp;·&nbsp; "
                    f"Avg Surprise: `{trend['avg_surprise_pct']:+.2f}%` &nbsp;·&nbsp; "
                    f"Beats: {trend['beat_count']} / Misses: {trend['miss_count']}")
        st.markdown(format_earnings_table(t_results))

    st.download_button("⬇ Download CSV", data=pd.DataFrame(rows).to_csv(index=False),
                       file_name="marketpulse_earnings.csv", mime="text/csv")
else:
    st.info("Enter earnings records and click **Compute Surprises**.")
