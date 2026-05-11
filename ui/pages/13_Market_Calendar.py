"""
Market Calendar Page — Streamlit UI for MarketPulse.

Shows upcoming earnings dates, ex-dividend dates, and US market holidays.
"""

import pandas as pd
import streamlit as st

from tools.market_calendar import (
    build_market_calendar,
    format_calendar_markdown,
    upcoming_earnings_list,
)

st.set_page_config(page_title="Market Calendar — MarketPulse", page_icon="📅", layout="wide")

st.markdown(
    """
    <style>
    .cal-header { background: linear-gradient(135deg,#1e1e2e,#1e2a3e);
      border:1px solid #89b4fa; border-radius:14px; padding:1.5rem 2rem; margin-bottom:1.5rem; }
    .cal-header h2 { color:#89b4fa; margin:0; }
    .ev-earn { border-left:4px solid #f38ba8; padding:.5rem 1rem; background:#2e1e2e;
               border-radius:0 8px 8px 0; margin:4px 0; }
    .ev-div  { border-left:4px solid #f9e2af; padding:.5rem 1rem; background:#2e2a1e;
               border-radius:0 8px 8px 0; margin:4px 0; }
    .ev-hol  { border-left:4px solid #89b4fa; padding:.5rem 1rem; background:#1e2a3e;
               border-radius:0 8px 8px 0; margin:4px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="cal-header"><h2>📅 Market Calendar</h2>'
    '<p style="color:#a6adc8;margin:0;">Upcoming earnings, ex-dividend dates, and US market holidays.</p></div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    raw = st.text_input("Tickers (comma-separated)", value="AAPL, MSFT, TSLA, NVDA", key="cal_tickers")
with c2:
    days_ahead = st.slider("Days ahead", 7, 90, 30)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("📅 Load Calendar", type="primary", use_container_width=True)

tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

if run_btn and tickers:
    from tools.stock_tools import get_stock_summary

    summaries = {}
    prog = st.progress(0, text="Fetching ticker data…")
    for i, t in enumerate(tickers):
        try:
            summaries[t] = get_stock_summary.invoke({"ticker": t})
        except Exception:
            summaries[t] = {}
        prog.progress((i + 1) / len(tickers), text=f"Fetched {t}")
    prog.empty()

    events   = build_market_calendar(summaries, include_holidays=True, days_ahead=days_ahead)
    earnings = upcoming_earnings_list(summaries, days_ahead=days_ahead)
    md_cal   = format_calendar_markdown(events)

    st.session_state["cal_events"]   = events
    st.session_state["cal_earnings"] = earnings
    st.session_state["cal_md"]       = md_cal

events   = st.session_state.get("cal_events")
earnings = st.session_state.get("cal_earnings", [])
md_cal   = st.session_state.get("cal_md", "")

if events is not None:
    n_earn = sum(1 for e in events if e["event_type"] == "earnings")
    n_div  = sum(1 for e in events if e["event_type"] == "ex_dividend")
    n_hol  = sum(1 for e in events if e["event_type"] == "holiday")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Events", len(events))
    m2.metric("📊 Earnings",  n_earn)
    m3.metric("💰 Dividends", n_div)
    m4.metric("🏖️ Holidays",  n_hol)

    st.divider()
    st.subheader("📋 Upcoming Events")

    css_map   = {"earnings": "ev-earn", "ex_dividend": "ev-div", "holiday": "ev-hol"}
    emoji_map = {"earnings": "📊", "ex_dividend": "💰", "holiday": "🏖️"}

    for e in events:
        css   = css_map.get(e["event_type"], "ev-hol")
        emoji = emoji_map.get(e["event_type"], "📌")
        tag   = f" — <b>{e['ticker']}</b>" if e.get("ticker") else ""
        st.markdown(
            f'<div class="{css}"><b>{e["date"]}</b>  {emoji} {e["description"]}{tag}</div>',
            unsafe_allow_html=True,
        )

    if earnings:
        st.divider()
        st.subheader("📊 Earnings Countdown")
        st.dataframe(pd.DataFrame(earnings), use_container_width=True)

    with st.expander("📅 Full Calendar Table"):
        df_all = pd.DataFrame([{
            "Date": e["date"], "Event": e["description"],
            "Ticker": e.get("ticker") or "—", "Type": e["event_type"],
            "Importance": e["importance"],
        } for e in events])
        st.dataframe(df_all, use_container_width=True)

    st.download_button("⬇ Download Calendar (Markdown)", data=md_cal,
                       file_name="marketpulse_calendar.md", mime="text/markdown", key="dl_cal_md")
else:
    st.info("Enter tickers and click **Load Calendar** to see upcoming market events.")
