"""
MarketPulse — World Market Index Scanner & Sentiment Tracker
Monitors global indices (US, Europe, Asia-Pacific) to gauge macro market regime.
"""

from typing import Any, Dict, List

WORLD_INDICES = {
    "^GSPC": {"name": "S&P 500", "region": "US"},
    "^IXIC": {"name": "Nasdaq Composite", "region": "US"},
    "^FTSE": {"name": "FTSE 100", "region": "UK/Europe"},
    "^N225": {"name": "Nikkei 225", "region": "Japan/Asia"},
    "^NSEI": {"name": "Nifty 50", "region": "India/Asia"},
}


def scan_world_markets() -> Dict[str, Any]:
    """
    Scans major global market indices and evaluates global macro regime.
    """
    results = {}
    positive_count = 0

    for symbol, info in WORLD_INDICES.items():
        try:
            import yfinance as yf
            ticker_obj = yf.Ticker(symbol)
            fast_info = ticker_obj.fast_info
            last_price = getattr(fast_info, "last_price", 0.0) or 0.0
            prev_close = getattr(fast_info, "previous_close", last_price) or last_price

            chg_pct = ((last_price - prev_close) / prev_close * 100.0) if prev_close else 0.0
            if chg_pct >= 0:
                positive_count += 1

            results[symbol] = {
                "name": info["name"],
                "region": info["region"],
                "price": round(float(last_price), 2),
                "change_pct": round(float(chg_pct), 2),
            }
        except Exception:
            results[symbol] = {
                "name": info["name"],
                "region": info["region"],
                "price": 0.0,
                "change_pct": 0.0,
            }

    ratio = positive_count / len(WORLD_INDICES)
    regime = "Risk-On (Bullish)" if ratio >= 0.6 else ("Risk-Off (Bearish)" if ratio <= 0.4 else "Neutral Macro")

    return {
        "indices": results,
        "macro_regime": regime,
        "positive_ratio": round(ratio, 2),
    }
