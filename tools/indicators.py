"""
Technical Indicators Module
Computes RSI, MACD, Bollinger Bands, and moving averages
from OHLCV price history data.
"""

from typing import Any, Dict, List

import pandas as pd


def compute_rsi(closes: List[float], period: int = 14) -> float:
    """
    Compute the Relative Strength Index (RSI) for a list of closing prices.

    Args:
        closes: List of closing prices (oldest first)
        period: RSI lookback period (default 14)

    Returns:
        RSI value between 0 and 100
    """
    if len(closes) < period + 1:
        return 50.0   # Neutral default if insufficient data

    series = pd.Series(closes)
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 2)


def compute_macd(
    closes: List[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Dict[str, float]:
    """
    Compute MACD line, signal line, and histogram.

    Returns:
        Dict with 'macd', 'signal', 'histogram', and 'crossover' keys
    """
    if len(closes) < slow + signal:
        return {"macd": 0.0, "signal": 0.0, "histogram": 0.0, "crossover": "Insufficient data"}

    series = pd.Series(closes)
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    macd_val = round(float(macd_line.iloc[-1]), 4)
    signal_val = round(float(signal_line.iloc[-1]), 4)
    hist_val = round(float(histogram.iloc[-1]), 4)

    crossover = "Bullish" if macd_val > signal_val else "Bearish"

    return {
        "macd": macd_val,
        "signal": signal_val,
        "histogram": hist_val,
        "crossover": crossover,
    }


def compute_bollinger_bands(
    closes: List[float], period: int = 20, std_dev: float = 2.0
) -> Dict[str, float]:
    """
    Compute Bollinger Bands (upper, middle, lower) for closing prices.

    Returns:
        Dict with 'upper', 'middle', 'lower', 'bandwidth', 'position' keys
    """
    if len(closes) < period:
        return {"upper": 0.0, "middle": 0.0, "lower": 0.0, "bandwidth": 0.0, "position": "N/A"}

    series = pd.Series(closes)
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()

    upper = sma + (std * std_dev)
    middle = sma
    lower = sma - (std * std_dev)

    curr_price = closes[-1]
    upper_val = round(float(upper.iloc[-1]), 2)
    mid_val = round(float(middle.iloc[-1]), 2)
    lower_val = round(float(lower.iloc[-1]), 2)
    bandwidth = round((upper_val - lower_val) / mid_val * 100, 2) if mid_val else 0.0

    # Determine price position within bands
    if curr_price >= upper_val:
        position = "Overbought"
    elif curr_price <= lower_val:
        position = "Oversold"
    else:
        position = "Within Bands"

    return {
        "upper": upper_val,
        "middle": mid_val,
        "lower": lower_val,
        "bandwidth": bandwidth,
        "position": position,
    }


def compute_moving_averages(closes: List[float]) -> Dict[str, Any]:
    """Compute SMA-20, SMA-50, EMA-12, EMA-26 and their trend signals."""
    series = pd.Series(closes)
    result: Dict[str, Any] = {}

    for period in [20, 50]:
        if len(closes) >= period:
            result[f"sma_{period}"] = round(float(series.rolling(period).mean().iloc[-1]), 2)
        else:
            result[f"sma_{period}"] = None

    for span in [12, 26]:
        if len(closes) >= span:
            result[f"ema_{span}"] = round(float(series.ewm(span=span).mean().iloc[-1]), 2)
        else:
            result[f"ema_{span}"] = None

    # Golden/Death cross signal
    sma20 = result.get("sma_20")
    sma50 = result.get("sma_50")
    if sma20 and sma50:
        result["ma_signal"] = "Golden Cross (Bullish)" if sma20 > sma50 else "Death Cross (Bearish)"
    else:
        result["ma_signal"] = "Insufficient data"

    return result


def get_all_indicators(price_history: List[Dict]) -> Dict[str, Any]:
    """
    Compute all technical indicators from a price history list.

    Args:
        price_history: List of OHLCV dicts (from get_price_history tool)

    Returns:
        Dict containing RSI, MACD, Bollinger Bands, and Moving Averages
    """
    if not price_history or "error" in price_history[0]:
        return {"error": "Insufficient price data for technical analysis"}

    closes = [r["close"] for r in price_history if "close" in r]

    return {
        "rsi": compute_rsi(closes),
        "rsi_signal": (
            "Overbought (RSI > 70)" if compute_rsi(closes) > 70
            else "Oversold (RSI < 30)" if compute_rsi(closes) < 30
            else "Neutral (RSI 30–70)"
        ),
        "macd": compute_macd(closes),
        "bollinger_bands": compute_bollinger_bands(closes),
        "moving_averages": compute_moving_averages(closes),
        "data_points": len(closes),
    }
