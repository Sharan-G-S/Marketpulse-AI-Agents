"""
Stock Market Data Tools
Wraps yfinance into LangChain-compatible @tool functions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from langchain_core.tools import tool
import pandas as pd
import yfinance as yf


@tool
def get_stock_summary(ticker: str) -> Dict[str, Any]:
    """
    Fetch real-time stock summary for a given ticker symbol.
    Returns price, market cap, PE ratio, 52-week high/low, and more.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker.upper(),
            "company_name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
            "previous_close": info.get("previousClose", 0),
            "open": info.get("open", 0),
            "day_high": info.get("dayHigh", 0),
            "day_low": info.get("dayLow", 0),
            "volume": info.get("volume", 0),
            "avg_volume": info.get("averageVolume", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", None),
            "eps": info.get("trailingEps", None),
            "52w_high": info.get("fiftyTwoWeekHigh", 0),
            "52w_low": info.get("fiftyTwoWeekLow", 0),
            "dividend_yield": info.get("dividendYield", None),
            "beta": info.get("beta", None),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "analyst_target_price": info.get("targetMeanPrice", None),
            "recommendation": info.get("recommendationKey", "N/A"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


@tool
def get_price_history(ticker: str, period: str = "1mo", interval: str = "1d") -> List[Dict[str, Any]]:
    """
    Fetch historical OHLCV price data for a ticker.
    period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
    interval options: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return []

        records = []
        for date, row in hist.iterrows():
            records.append({
                "date": str(date.date()),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })
        return records
    except Exception as e:
        return [{"error": str(e)}]


@tool
def get_financials(ticker: str) -> Dict[str, Any]:
    """
    Fetch key financial statements for a ticker (income statement, balance sheet summary).
    """
    try:
        stock = yf.Ticker(ticker)
        income = stock.income_stmt

        if income is None or income.empty:
            return {"error": "No financial data available"}

        latest = income.iloc[:, 0]
        return {
            "total_revenue": latest.get("Total Revenue", None),
            "gross_profit": latest.get("Gross Profit", None),
            "operating_income": latest.get("Operating Income", None),
            "net_income": latest.get("Net Income", None),
            "ebitda": latest.get("EBITDA", None),
            "period": str(income.columns[0].date()) if not income.empty else "N/A",
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def calculate_price_change(price_history: List[Dict]) -> Dict[str, Any]:
    """
    Calculate percentage price change, momentum, and trend from price history.
    """
    try:
        if not price_history or "error" in price_history[0]:
            return {"error": "Invalid price history"}

        closes = [r["close"] for r in price_history if "close" in r]
        if len(closes) < 2:
            return {"error": "Insufficient data"}

        first, last = closes[0], closes[-1]
        change_pct = round(((last - first) / first) * 100, 2)

        # Simple momentum: compare last 5 days vs rest
        recent = closes[-5:] if len(closes) >= 5 else closes
        momentum = "Upward" if recent[-1] > recent[0] else "Downward"

        return {
            "start_price": first,
            "end_price": last,
            "change_pct": change_pct,
            "trend": "Bullish" if change_pct > 0 else "Bearish",
            "momentum": momentum,
            "highest": max(closes),
            "lowest": min(closes),
            "volatility": round(pd.Series(closes).std(), 2),
        }
    except Exception as e:
        return {"error": str(e)}
