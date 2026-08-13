"""
Technical Indicators Module
Computes RSI, MACD, Bollinger Bands, and moving averages
from OHLCV price history data with division by zero guards.
"""

from typing import Any, Dict, List, Optional
import pandas as pd

from tools.fibonacci import calculate_fibonacci_levels
from tools.momentum import get_momentum_summary


def compute_rsi(closes: List[float], period: int = 14) -> float:
    """
    Compute Relative Strength Index (RSI) with zero-gain/loss bounds safety.
    """
    if not closes or len(closes) < period + 1:
        return 50.0

    series = pd.Series(closes)
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    if avg_loss.iloc[-1] == 0:
        return 100.0 if avg_gain.iloc[-1] > 0 else 50.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    val = float(rsi.iloc[-1])
    if pd.isna(val):
        return 50.0
    return round(val, 2)


def compute_macd(
    closes: List[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Dict[str, float]:
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
    if not closes or len(closes) < period:
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
    if not price_history or len(price_history) < k_period:
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

    sma20 = result.get("sma_20")
    sma50 = result.get("sma_50")
    if sma20 and sma50:
        result["ma_signal"] = "Golden Cross (Bullish)" if sma20 > sma50 else "Death Cross (Bearish)"
    else:
        result["ma_signal"] = "Insufficient data"

    return result


def compute_atr(price_history: List[Dict], period: int = 14) -> Dict[str, Any]:
    if not price_history or len(price_history) < period + 1:
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


def compute_vwap(price_history: List[Dict]) -> float:
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


def compute_obv(price_history: List[Dict]) -> float:
    if not price_history:
        return 0.0
    obv = 0.0
    for i in range(1, len(price_history)):
        curr = price_history[i].get("close", 0)
        prev = price_history[i - 1].get("close", 0)
        vol = price_history[i].get("volume", 0)
        if curr > prev:
            obv += vol
        elif curr < prev:
            obv -= vol
    return round(obv, 2)


def get_all_indicators(price_history: List[Dict]) -> Dict[str, Any]:
    if not price_history or "error" in price_history[0]:
        return {"error": "Insufficient price data for technical analysis"}

    closes = [r["close"] for r in price_history if isinstance(r, dict) and "close" in r]
    if not closes:
        return {"error": "No close prices available in history"}

    rsi_val = compute_rsi(closes)
    return {
        "rsi": rsi_val,
        "rsi_signal": (
            "Overbought (RSI > 70)" if rsi_val > 70
            else "Oversold (RSI < 30)" if rsi_val < 30
            else "Neutral (RSI 30-70)"
        ),
        "macd": compute_macd(closes),
        "bollinger_bands": compute_bollinger_bands(closes),
        "moving_averages": compute_moving_averages(closes),
        "stochastic": compute_stochastic_oscillator(price_history),
        "atr": compute_atr(price_history),
        "vwap": compute_vwap(price_history),
        "obv": compute_obv(price_history),
        "fibonacci": calculate_fibonacci_levels(price_history),
        "momentum": get_momentum_summary(price_history) if price_history else {},
        "data_points": len(closes),
    }
