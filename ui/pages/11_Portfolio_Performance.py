"""
Portfolio Performance Page — Streamlit UI for MarketPulse.

Users enter positions (ticker, shares, avg cost), the app fetches live
prices and displays P&L, weights, and a performance breakdown table.
"""

import pandas as pd
import streamlit as st

from tools.portfolio_performance import (
    compute_portfolio,
    sector_allocation,
    top_holdings,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Portfolio Performance — MarketPulse",
    page_icon="💼",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .port-header {
        background: linear-gradient(135deg, #1e2a1e 0%, #2a3a2e 100%);
        border: 1px solid #a6e3a1;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .port-header h2 { color: #a6e3a1; margin: 0; }
    .gain  { color: #a6e3a1; font-weight: 700; }
    .loss  { color: #f38ba8; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="port-header">
        <h2>💼 Portfolio Performance</h2>
        <p style="color:#a6adc8;margin:0;">
        Enter your holdings, fetch live prices, and track P&amp;L in real time.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Position entry ────────────────────────────────────────────────────────────

st.subheader("📋 Enter Positions")

st.caption(
    "Format each row as  **TICKER, shares, avg_cost**  (one per line). "
    "Example:  `AAPL, 10, 145.50`"
)

default_positions = "AAPL, 10, 145.50\nMSFT, 5, 280.00\nTSLA, 8, 210.00\nNVDA, 3, 450.00"

raw_input = st.text_area(
    "Positions",
    value=default_positions,
    height=150,
    key="port_positions",
)

# ── Parse positions ───────────────────────────────────────────────────────────

positions = []
parse_errors = []
for line in raw_input.strip().splitlines():
    line = line.strip()
    if not line:
        continue
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 3:
        parse_errors.append(f"⚠️ Skipped (invalid format): `{line}`")
        continue
    try:
        positions.append({
            "ticker":   parts[0].upper(),
            "qty":      float(parts[1]),
            "avg_cost": float(parts[2]),
        })
    except ValueError:
        parse_errors.append(f"⚠️ Skipped (non-numeric qty/cost): `{line}`")

for err in parse_errors:
    st.warning(err)

# ── Fetch & compute ───────────────────────────────────────────────────────────

run_btn = st.button("📈 Fetch Prices & Compute P&L", type="primary")

if run_btn and positions:
    from tools.stock_tools import get_stock_summary

    price_map = {}
    prog = st.progress(0, text="Fetching live prices…")
    tickers = [p["ticker"] for p in positions]

    for i, t in enumerate(tickers):
        try:
            summary = get_stock_summary.invoke({"ticker": t})
            price = summary.get("current_price") or summary.get("regularMarketPrice")
            if price:
                price_map[t] = float(price)
        except Exception:
            pass
        prog.progress((i + 1) / len(tickers), text=f"Fetched {t}")

    prog.empty()

    summary = compute_portfolio(positions, price_map)
    st.session_state["port_summary"]  = summary
    st.session_state["port_price_map"] = price_map

summary = st.session_state.get("port_summary")

if summary:
    total_mv  = summary["total_market_value"]
    total_pl  = summary["total_unrealised_pl"]
    total_ret = summary["total_return_pct"]
    pl_sign   = "gain" if total_pl >= 0 else "loss"

    # ── Top metrics ───────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Market Value", f"${total_mv:,.2f}")
    m2.metric(
        "Unrealised P&L",
        f"${total_pl:+,.2f}",
        delta=f"{total_ret:+.2f}%",
        delta_color="normal",
    )
    m3.metric("Best Performer",  summary["best_performer"])
    m4.metric("Worst Performer", summary["worst_performer"])

    st.divider()

    # ── Position table ────────────────────────────────────────────────────────
    st.subheader("📊 Position Breakdown")
    rows = []
    for r in summary["positions"]:
        rows.append({
            "Ticker":    r["ticker"],
            "Shares":    r["qty"],
            "Avg Cost":  f"${r['avg_cost']:.2f}",
            "Price":     f"${r['current_price']:.2f}",
            "Mkt Value": f"${r['market_value']:,.2f}",
            "P&L":       f"${r['unrealised_pl']:+,.2f}",
            "Return %":  f"{r['unrealised_pct']:+.2f}%",
            "Weight %":  f"{r['weight_pct']:.2f}%",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.divider()

    # ── Top holdings bar chart ────────────────────────────────────────────────
    st.subheader("🏆 Top Holdings by Market Value")
    top = top_holdings(summary, n=10)
    df_top = pd.DataFrame(
        {"Market Value": [r["market_value"] for r in top]},
        index=[r["ticker"] for r in top],
    )
    st.bar_chart(df_top, height=250)

    st.divider()

    # ── Download ──────────────────────────────────────────────────────────────
    csv_rows = [
        {
            "Ticker":       r["ticker"],
            "Qty":          r["qty"],
            "Avg Cost":     r["avg_cost"],
            "Current Price":r["current_price"],
            "Market Value": r["market_value"],
            "P&L":          r["unrealised_pl"],
            "Return %":     r["unrealised_pct"],
            "Weight %":     r["weight_pct"],
        }
        for r in summary["positions"]
    ]
    csv = pd.DataFrame(csv_rows).to_csv(index=False)
    st.download_button(
        "⬇ Download Portfolio CSV",
        data=csv,
        file_name="marketpulse_portfolio.csv",
        mime="text/csv",
        key="dl_port_csv",
    )

else:
    st.info("Enter your positions and click **Fetch Prices & Compute P&L** to begin.")
