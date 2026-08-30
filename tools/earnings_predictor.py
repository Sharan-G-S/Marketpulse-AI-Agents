"""
MarketPulse — Corporate Earnings Beat Probability Estimator
Estimates probability of upcoming quarterly EPS beat based on historical track record.
"""

from typing import Any, Dict, List


def estimate_earnings_beat_probability(historical_surprises: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes earnings beat probability percentage and trend label.
    """
    if not historical_surprises:
        return {"beat_probability_pct": 50.0, "beat_rate_label": "Neutral / Unknown Track Record"}

    beats = 0
    total = len(historical_surprises)

    for item in historical_surprises:
        actual = item.get("actual", 0.0) or 0.0
        estimate = item.get("estimate", 0.0) or 0.0
        if actual > estimate:
            beats += 1

    beat_rate = round((beats / total) * 100.0, 1)

    if beat_rate >= 75.0:
        label = "High Probability Beat (Consistent Outperformer)"
    elif beat_rate >= 50.0:
        label = "Moderate Beat Likelihood"
    else:
        label = "High Miss Risk (Inconsistent Results)"

    return {
        "beat_probability_pct": beat_rate,
        "historical_quarters_analyzed": total,
        "quarters_beat": beats,
        "beat_rate_label": label,
    }
