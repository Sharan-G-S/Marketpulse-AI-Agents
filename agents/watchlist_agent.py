"""
Watchlist Agent — Monitors multiple tickers simultaneously
and generates a comparative market intelligence summary.

Now includes Alert Engine integration: price, RSI, and percentage-change
alerts are evaluated after each watchlist scan and stored in state.
"""

from typing import Any, Dict, List

from agents.alert_engine import AlertEngine
from agents.alert_helpers import format_alert_digest
from graph.state import MarketPulseState
from tools.indicators import compute_rsi, get_all_indicators
from tools.stock_tools import calculate_price_change, get_price_history, get_stock_summary

WATCHLIST_DEFAULTS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "NFLX"]


def watchlist_agent(state: MarketPulseState) -> MarketPulseState:
    """
    Watchlist Agent Node.

    Scans a predefined list of top tickers and enriches the shared
    state with a comparative market overview table.
    """
    ticker = state.get("ticker", "AAPL")
    print(f"\n[📋 Watchlist Agent] Building market watchlist context...")

    watchlist_data: List[Dict[str, Any]] = []
    market_snapshot: Dict[str, Dict[str, Any]] = {}  # for alert evaluation

    # Include the main ticker + a small sample of top stocks for context
    scan_list = list({ticker}.union(set(WATCHLIST_DEFAULTS[:5])))

    for t in scan_list:
        try:
            summary = get_stock_summary.invoke({"ticker": t})
            history = get_price_history.invoke({"ticker": t, "period": "1mo", "interval": "1d"})
            metrics = calculate_price_change.invoke({"price_history": history})
            indicators = get_all_indicators(history)

            entry = {
                "ticker": t,
                "price": summary.get("current_price", 0),
                "change_pct": metrics.get("change_pct", 0),
                "trend": metrics.get("trend", "N/A"),
                "market_cap": summary.get("market_cap", 0),
                "pe_ratio": summary.get("pe_ratio", "N/A"),
                "sector": summary.get("sector", "N/A"),
                "rsi": indicators.get("rsi"),
                "rsi_signal": indicators.get("rsi_signal"),
            }
            watchlist_data.append(entry)

            # Build market snapshot for alert evaluation
            market_snapshot[t] = {
                "current_price": summary.get("current_price"),
                "change_pct": metrics.get("change_pct"),
                "rsi": indicators.get("rsi"),
            }
        except Exception as e:
            watchlist_data.append({"ticker": t, "error": str(e)})

    # Sort by absolute price change
    watchlist_data.sort(key=lambda x: abs(x.get("change_pct", 0)), reverse=True)

    # --- Alert Engine evaluation ---
    alert_engine = AlertEngine.with_default_rules(scan_list)
    triggered_alerts = alert_engine.evaluate(market_snapshot)
    alert_digest = format_alert_digest(triggered_alerts)
    n_alerts = len(triggered_alerts)
    print(f"[📋 Watchlist Agent] ✅ Scanned {len(watchlist_data)} tickers. "
          f"{n_alerts} alert(s) triggered.")

    return {
        **state,
        "messages": state.get("messages", []) + [
            f"[Watchlist Agent] Scanned {len(watchlist_data)} tickers. "
            f"{n_alerts} alert(s) triggered."
        ],
        # Store in stock_summary for downstream access
        "stock_summary": {
            **state.get("stock_summary", {}),
            "watchlist": watchlist_data,
            "alerts": [
                {
                    "ticker": a.rule.ticker,
                    "type": a.rule.alert_type.value,
                    "severity": a.severity.value,
                    "message": a.message,
                    "current_value": a.current_value,
                    "triggered_at": a.triggered_at,
                }
                for a in triggered_alerts
            ],
            "alert_digest": alert_digest,
        },
    }


def format_watchlist_table(watchlist: List[Dict[str, Any]]) -> str:
    """Format the watchlist data as a markdown table."""
    rows = ["| Ticker | Price | Change | Trend | PE | Sector |",
            "|--------|-------|--------|-------|----|--------|"]
    for item in watchlist:
        if "error" in item:
            rows.append(f"| {item['ticker']} | — | — | Error | — | — |")
            continue
        chg = item.get("change_pct", 0)
        emoji = "🟢" if chg > 0 else "🔴" if chg < 0 else "⚪"
        rows.append(
            f"| **{item['ticker']}** | ${item.get('price', 0):.2f} | "
            f"{emoji} {chg:+.2f}% | {item.get('trend', 'N/A')} | "
            f"{item.get('pe_ratio', 'N/A')} | {item.get('sector', 'N/A')} |"
        )
    return "\n".join(rows)
