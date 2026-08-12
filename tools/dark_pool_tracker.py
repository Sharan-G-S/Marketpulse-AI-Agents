"""
MarketPulse — Dark Pool & Institutional Volume Anomaly Tracker
Detects large institutional block trade volume spikes and off-exchange activity anomalies.
"""

from typing import Any, Dict


def detect_dark_pool_activity(current_volume: int, avg_volume: int) -> Dict[str, Any]:
    """
    Detects institutional dark pool volume anomalies.

    Args:
        current_volume: Current trading volume
        avg_volume: 30-day average volume

    Returns:
        Dict with volume_ratio, is_anomaly (True/False), and signal level.
    """
    if not avg_volume or avg_volume <= 0:
        return {"volume_ratio": 1.0, "is_anomaly": False, "signal": "Normal Volume"}

    ratio = current_volume / avg_volume

    if ratio >= 3.0:
        signal = "Extreme Institutional Dark Pool Accumulation (3.0x+)"
        is_anomaly = True
    elif ratio >= 2.0:
        signal = "High Institutional Block Trade Volume (2.0x+)"
        is_anomaly = True
    elif ratio <= 0.3:
        signal = "Unusually Low Volume Liquidity Drawdown"
        is_anomaly = True
    else:
        signal = "Normal Trading Volume Range"
        is_anomaly = False

    return {
        "volume_ratio": round(float(ratio), 2),
        "is_anomaly": is_anomaly,
        "signal": signal,
    }
