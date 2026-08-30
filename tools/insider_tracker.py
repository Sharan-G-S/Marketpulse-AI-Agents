"""
MarketPulse — Institutional Ownership & Insider Buy/Sell Scanner
Evaluates Form 4 insider transactions to gauge C-suite executive confidence.
"""

from typing import Any, Dict, List


def analyze_insider_activity(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes net insider buying vs selling shares and sentiment.
    """
    if not transactions:
        return {"net_insider_sentiment": "Neutral", "total_buy_shares": 0, "total_sell_shares": 0}

    buy_shares = 0
    sell_shares = 0

    for tx in transactions:
        tx_type = tx.get("type", "").upper()
        shares = int(tx.get("shares", 0) or 0)
        if "BUY" in tx_type or "PURCHASE" in tx_type:
            buy_shares += shares
        elif "SELL" in tx_type or "SALE" in tx_type:
            sell_shares += shares

    net_shares = buy_shares - sell_shares

    if net_shares > 0:
        sentiment = "Bullish Insider Buying (Net Accumulation)"
    elif net_shares < 0:
        sentiment = "Bearish Insider Selling (Net Distribution)"
    else:
        sentiment = "Neutral Insider Activity"

    return {
        "net_insider_sentiment": sentiment,
        "total_buy_shares": buy_shares,
        "total_sell_shares": sell_shares,
        "net_shares_change": net_shares,
    }
