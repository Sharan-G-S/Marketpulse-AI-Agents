"""
Stock Data Agent
Fetches real-time and historical stock data using yfinance tools
and enriches the shared state with market data.
"""

from graph.state import MarketPulseState
from tools.stock_tools import get_stock_summary, get_price_history, calculate_price_change
from config.settings import DEFAULT_PERIOD, DEFAULT_INTERVAL


def stock_data_agent(state: MarketPulseState) -> MarketPulseState:
    """
    Stock Data Agent Node.

    Fetches current stock price, historical OHLCV data, and
    calculates price trend metrics for the target ticker.
    """
    ticker = state["ticker"]
    company_name = state["company_name"]
    depth = state.get("analysis_depth", "standard")

    print(f"\n[📈 Stock Agent] Fetching market data for {ticker}...")

    # Determine period based on analysis depth
    period_map = {"quick": "5d", "standard": "1mo", "deep": "3mo"}
    period = period_map.get(depth, DEFAULT_PERIOD)

    # ── Fetch data using tools ─────────────────────────────────────────────────
    stock_summary = get_stock_summary.invoke({"ticker": ticker})
    price_history = get_price_history.invoke({
        "ticker": ticker,
        "period": period,
        "interval": DEFAULT_INTERVAL,
    })

    # ── Calculate trend metrics ────────────────────────────────────────────────
    if price_history and "error" not in price_history[0]:
        price_metrics = calculate_price_change.invoke({"price_history": price_history})
        stock_summary.update(price_metrics)

    # ── Log key metrics ───────────────────────────────────────────────────────
    current_price = stock_summary.get("current_price", 0)
    change_pct = stock_summary.get("change_pct", 0)
    trend = stock_summary.get("trend", "N/A")

    print(f"[📈 Stock Agent] ✅ {ticker}: ${current_price:.2f} | {change_pct:+.2f}% | Trend: {trend}")

    return {
        **state,
        "stock_summary": stock_summary,
        "price_history": price_history,
        "stock_fetched": True,
        "messages": [
            f"[Stock Agent] {ticker} @ ${current_price:.2f} ({change_pct:+.2f}% over {period}). "
            f"Trend: {trend}."
        ],
    }
