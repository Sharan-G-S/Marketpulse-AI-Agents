"""
MarketPulse — Adaptive Volatility-Based Cache Policy
Dynamically calculates cache TTL based on asset volatility regime (high volatility = short TTL).
"""

from typing import Any, Dict


def get_adaptive_ttl(volatility_label: str = "Moderate Volatility", default_ttl: int = 300) -> int:
    """
    Returns dynamically adjusted TTL in seconds based on market volatility label.
    """
    if "High" in volatility_label:
        return 60   # 1 min cache during high volatility
    elif "Low" in volatility_label:
        return 900  # 15 min cache during low volatility
    return default_ttl
