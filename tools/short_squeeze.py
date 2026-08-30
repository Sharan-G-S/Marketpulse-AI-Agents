"""
MarketPulse — Short Squeeze Risk Score & Days-to-Cover Calculator
Evaluates short interest float percentage and days-to-cover for squeeze potential.
"""

from typing import Any, Dict


def calculate_short_squeeze_risk(short_float_pct: float, days_to_cover: float) -> Dict[str, Any]:
    """
    Computes Short Squeeze Score (0-100) and risk tier.
    """
    sf = max(0.0, float(short_float_pct))
    dtc = max(0.0, float(days_to_cover))

    score = round(min(100.0, (sf * 2.5) + (dtc * 5.0)), 1)

    if score >= 70.0:
        tier = "High Squeeze Potential (Heavy Short Interest & Days-to-Cover)"
    elif score >= 40.0:
        tier = "Moderate Squeeze Potential"
    else:
        tier = "Low Squeeze Potential"

    return {
        "short_float_pct": sf,
        "days_to_cover": dtc,
        "squeeze_score": score,
        "squeeze_tier": tier,
    }
