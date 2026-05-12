"""MA Crossover Signals — Streamlit page for MarketPulse."""

import pandas as pd
import streamlit as st

from tools.ma_crossover import ma_crossover_summary

st.set_page_config(page_title="MA Crossover — MarketPulse", page_icon="📉", layout="wide")

st.markdown("""
<style>
.ma-header { background: linear-gradient(135deg,#1e1e2e,#1e2e2a);
  border:1px solid #94e2d5; border-radius:14px; padding:1.5rem 2rem; margin-bottom:1.5rem; }
.ma-header h2 { color:#94e2d5; margin:0; }
.bull { color:#a6e3a1; font-weight:700; }
.bear { color:#f38ba8; font-weight:700; }
</style>""", unsafe_allow_html=True)

st.markdown(
    '<div class="ma-header"><h2>📉 MA Crossover Signals</h2>'
    '<p style="color:#a6adc8;margin:0;">Detect Golden Cross and Death Cross events for any ticker.</p></div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
with c1:
    raw = st.text_input("Tickers (comma-separated)", value="AAPL, MSFT, TSLA", key="ma_tickers")
with c2:
    fast = st.number_input("Fast Period", min_value=5, max_value=100, value=50, step=5)
with c3:
    slow = st.number_input("Slow Period", min_value=20, max_value=400, value=200, step=10)
with c4:
    use_ema = st.checkbox("Use EMA", value=False)
with c5:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("📉 Compute Signals", type="primary", use_container_width=True)

tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

if run_btn and tickers:
    from tools.stock_tools import get_price_history

    summaries = {}
    prog = st.progress(0, text="Fetching price history…")
    for i, t in enumerate(tickers):
        try:
            hist = get_price_history.invoke({"ticker": t, "period": "1y", "interval": "1d"})
            summaries[t] = ma_crossover_summary(hist, fast_period=fast, slow_period=slow, use_ema=use_ema)
        except Exception as ex:
            summaries[t] = {"current_signal": f"Error: {ex}", "crossover_events": []}
        prog.progress((i + 1) / len(tickers), text=f"Computed {t}")
    prog.empty()
    st.session_state["ma_summaries"] = summaries

summaries = st.session_state.get("ma_summaries", {})

if summaries:
    st.divider()
    st.subheader("📋 Signal Summary")

    rows = []
    for t, s in summaries.items():
        css = "bull" if "Bullish" in s.get("current_signal", "") else (
              "bear" if "Bearish" in s.get("current_signal", "") else "")
        label = s.get("current_signal", "—")
        st.markdown(
            f"**{t}** — <span class='{css}'>{label}</span>  "
            f"| Fast MA: `{s.get('fast_value') or '—'}` "
            f"| Slow MA: `{s.get('slow_value') or '—'}` "
            f"| Crossovers: {len(s.get('crossover_events', []))}",
            unsafe_allow_html=True,
        )
        rows.append({
            "Ticker":     t,
            "Signal":     label,
            "Fast MA":    s.get("fast_value"),
            "Slow MA":    s.get("slow_value"),
            "N Crossovers": len(s.get("crossover_events", [])),
            "Last Crossover": (s.get("last_crossover") or {}).get("signal", "—"),
        })

    st.divider()
    st.subheader("📊 Crossover Events Detail")
    for t, s in summaries.items():
        events = s.get("crossover_events", [])
        if events:
            with st.expander(f"{t} — {len(events)} crossover(s)"):
                st.dataframe(pd.DataFrame(events), use_container_width=True)

    df = pd.DataFrame(rows)
    st.divider()
    st.dataframe(df, use_container_width=True)
else:
    st.info("Enter tickers and click **Compute Signals**.")
