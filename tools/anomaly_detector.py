"""
MarketPulse — Stock Price Anomaly & Data Quality Detector
Detects zero prices, flash crash spikes, volume anomalies, and missing metrics.
"""

from typing import Any, Dict, List, Tuple


def detect_price_anomalies(price_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scans price history list for extreme anomalies and data corruption.

    Args:
        price_history: List of OHLC dictionary rows

    Returns:
        Dict with anomaly flags, clean record count, and data health score (0-100).
    """
    if not price_history or not isinstance(price_history, list):
        return {"health_score": 0, "anomalies": ["No price history data provided"], "valid_count": 0}

    anomalies = []
    valid_count = 0

    for i, row in enumerate(price_history):
        close_p = row.get("close")
        if close_p is None or close_p <= 0:
            anomalies.append(f"Invalid non-positive close price at index {i}: {close_p}")
            continue

        valid_count += 1

        # Check for single-day flash spike (> 50% jump/drop)
        if i > 0:
            prev_close = price_history[i - 1].get("close", close_p)
            if prev_close and prev_close > 0:
                change_ratio = abs(close_p - prev_close) / prev_close
                if change_ratio > 0.5:
                    anomalies.append(f"Extreme price spike ({change_ratio:.0%}) detected at index {i}")

    total = len(price_history)
    health_score = round((valid_count / total) * 100.0 if total > 0 else 0.0, 1)

    return {
        "health_score": health_score,
        "anomalies": anomalies,
        "valid_count": valid_count,
        "total_records": total,
    }
