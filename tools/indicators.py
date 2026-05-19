"""
Technical Indicators Module
Computes RSI, MACD, Bollinger Bands, and moving averages
from OHLCV price history data.
"""

from typing import Any, Dict, List, Optional

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
    if not closes or len(closes) < slow + signal:
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


def compute_stochastic_oscillator(
    price_history: List[Dict],
    k_period: int = 14,
    d_period: int = 3,
) -> Dict[str, Any]:
    """
    Compute the Stochastic Oscillator (%K and %D lines).

    %K = (Close - Lowest Low) / (Highest High - Lowest Low) * 100
    %D = Simple moving average of %K over d_period bars.

    Args:
        price_history: List of OHLCV dicts with 'high', 'low', 'close' keys.
        k_period: Lookback period for %K (default 14).
        d_period: Smoothing period for %D (default 3).

    Returns:
        Dict with 'k', 'd', 'signal' and 'zone' keys.
    """
    if len(price_history) < k_period:
        return {"k": None, "d": None, "signal": "Insufficient data", "zone": "N/A"}

    try:
        highs = [r["high"] for r in price_history]
        lows = [r["low"] for r in price_history]
        closes = [r["close"] for r in price_history]

        k_values: List[Optional[float]] = []
        for i in range(len(closes)):
            if i < k_period - 1:
                k_values.append(None)
                continue
            window_highs = highs[i - k_period + 1: i + 1]
            window_lows = lows[i - k_period + 1: i + 1]
            highest_high = max(window_highs)
            lowest_low = min(window_lows)
            denom = highest_high - lowest_low
            if denom == 0:
                k_values.append(50.0)
            else:
                k_values.append((closes[i] - lowest_low) / denom * 100)

        valid_k = [v for v in k_values if v is not None]
        if len(valid_k) < d_period:
            return {"k": None, "d": None, "signal": "Insufficient data", "zone": "N/A"}

        k_val = round(valid_k[-1], 2)
        d_val = round(sum(valid_k[-d_period:]) / d_period, 2)

        if k_val >= 80:
            zone = "Overbought"
        elif k_val <= 20:
            zone = "Oversold"
        else:
            zone = "Neutral"

        signal = "Bullish" if k_val > d_val else "Bearish"

        return {"k": k_val, "d": d_val, "signal": signal, "zone": zone}
    except (KeyError, TypeError, ValueError):
        return {"k": None, "d": None, "signal": "Error", "zone": "N/A"}


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


def compute_atr(price_history: List[Dict], period: int = 14) -> Dict[str, Any]:
    """
    Compute the Average True Range (ATR) for measuring price volatility.

    True Range is max(High-Low, |High-PrevClose|, |Low-PrevClose|).
    ATR is the exponential moving average of True Range over `period` bars.

    Args:
        price_history: List of OHLCV dicts with 'high', 'low', 'close' keys.
        period: ATR lookback period (default 14).

    Returns:
        Dict with 'atr', 'atr_pct' (relative to last close), and 'volatility_label'.
    """
    if len(price_history) < period + 1:
        return {"atr": None, "atr_pct": None, "volatility_label": "Insufficient data"}

    try:
        true_ranges: List[float] = []
        for i in range(1, len(price_history)):
            high = price_history[i]["high"]
            low = price_history[i]["low"]
            prev_close = price_history[i - 1]["close"]
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)

        if len(true_ranges) < period:
            return {"atr": None, "atr_pct": None, "volatility_label": "Insufficient data"}

        atr_series = pd.Series(true_ranges)
        atr_val = round(float(atr_series.ewm(com=period - 1, min_periods=period).mean().iloc[-1]), 4)
        last_close = price_history[-1]["close"]
        atr_pct = round(atr_val / last_close * 100, 2) if last_close else None

        if atr_pct is None:
            volatility_label = "N/A"
        elif atr_pct >= 3.0:
            volatility_label = "High Volatility"
        elif atr_pct >= 1.5:
            volatility_label = "Moderate Volatility"
        else:
            volatility_label = "Low Volatility"

        return {"atr": atr_val, "atr_pct": atr_pct, "volatility_label": volatility_label}
    except (KeyError, TypeError, ValueError):
        return {"atr": None, "atr_pct": None, "volatility_label": "Error"}

def get_all_indicators(price_history: List[Dict]) -> Dict[str, Any]:
    """
    Compute all technical indicators from a price history list.

    Args:
        price_history: List of OHLCV dicts (from get_price_history tool)

    Returns:
        Dict containing RSI, MACD, Bollinger Bands, Moving Averages,
        Stochastic Oscillator, and Average True Range.
    """
    if not price_history or "error" in price_history[0]:
        return {"error": "Insufficient price data for technical analysis"}

    closes = [r["close"] for r in price_history if "close" in r]
    if not closes:
        return {"error": "No close prices available in history"}

    return {
        "rsi": compute_rsi(closes),
        "rsi_signal": (
            "Overbought (RSI > 70)" if compute_rsi(closes) > 70
            else "Oversold (RSI < 30)" if compute_rsi(closes) < 30
            else "Neutral (RSI 30-70)"
        ),
        "macd": compute_macd(closes),
        "bollinger_bands": compute_bollinger_bands(closes),
        "moving_averages": compute_moving_averages(closes),
        "stochastic": compute_stochastic_oscillator(price_history),
        "atr": compute_atr(price_history),
        "vwap": compute_vwap(price_history),
        "data_points": len(closes),
    }

def compute_vwap(price_history: List[Dict]) -> float:
    """Compute Volume Weighted Average Price (VWAP)."""
    if not price_history:
        return 0.0
    cumulative_pv = 0.0
    cumulative_volume = 0.0
    for row in price_history:
        high = row.get("high", row.get("close", 0))
        low = row.get("low", row.get("close", 0))
        close = row.get("close", 0)
        volume = row.get("volume", 0)
        typical_price = (high + low + close) / 3
        cumulative_pv += typical_price * volume
        cumulative_volume += volume
    if cumulative_volume == 0:
        return 0.0
    return round(cumulative_pv / cumulative_volume, 2)
