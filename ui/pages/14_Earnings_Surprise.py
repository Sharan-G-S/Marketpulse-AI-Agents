"""
Earnings Surprise Tracker — Streamlit Page for MarketPulse.
Track EPS beats, misses, & surprise percentages in Claude theme.
"""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.theme import apply_claude_theme, render_claude_header, CLAUDE_COLORS
from tools.earnings_surprise import compute_earnings_history, earnings_trend

st.set_page_config(page_title="Earnings Surprise — MarketPulse", page_icon="📊", layout="wide")
apply_claude_theme()

render_claude_header(
    title="Earnings Surprise & EPS Beat/Miss Tracker",
    subtitle="Evaluate quarterly reported EPS against consensus estimates and compute historical beat rate",
    icon="📊"
)

default_data = (
    "AAPL, Q1 2026, 2.20, 2.00\n"
    "AAPL, Q4 2025, 2.10, 2.15\n"
    "AAPL, Q3 2025, 1.96, 1.80\n"
    "MSFT, Q1 2026, 3.45, 3.10\n"
    "TSLA, Q1 2026, 0.45, 0.55\n"
)

st.markdown("<div class='claude-card-title'>📋 Earnings History Entry</div>", unsafe_allow_html=True)
raw = st.text_area("Format: TICKER, Period, Reported EPS, Estimated EPS", value=default_data, height=140)
run_btn = st.button("📊 Compute EPS Surprises", use_container_width=True)

records = []
for line in raw.strip().splitlines():
    parts = [p.strip() for p in line.split(",") if p.strip()]
    if len(parts) >= 4:
        try:
            records.append({
                "ticker": parts[0].upper(),
                "period": parts[1],
                "reported_eps": float(parts[2]),
                "estimated_eps": float(parts[3]),
            })
        except ValueError:
            pass

if run_btn or "earn_results" in st.session_state:
    if run_btn and records:
        results = compute_earnings_history(records)
        st.session_state["earn_results"] = results

    results = st.session_state.get("earn_results", [])
    if results:
        st.markdown("<div class='claude-card-title'>📈 Quarterly EPS Beat / Miss Results</div>", unsafe_allow_html=True)
        rows = [{
            "Ticker": r["ticker"],
            "Period": r["period"],
            "Reported EPS": f"${r['reported_eps']:.2f}",
            "Est. EPS": f"${r['estimated_eps']:.2f}",
            "Surprise %": f"{r['eps_surprise_pct']:+.2f}%",
            "Verdict": r["eps_verdict"],
        } for r in results]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("Click 'Compute EPS Surprises' to calculate beat/miss statistics.")
