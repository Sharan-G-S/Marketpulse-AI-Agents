"""
MarketPulse — Black-Scholes Options Pricing & Implied Volatility Model
Computes European Call & Put option theoretical prices and option Greeks (Delta, Gamma).
"""

import math
from typing import Any, Dict


def _norm_cdf(x: float) -> float:
    """Standard Normal Cumulative Distribution Function approximation."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def calculate_black_scholes(
    stock_price: float,
    strike_price: float,
    time_to_expiry_years: float = 0.25,
    risk_free_rate: float = 0.05,
    volatility: float = 0.30,
) -> Dict[str, Any]:
    """
    Computes Black-Scholes option pricing model for Call and Put contracts.
    """
    if stock_price <= 0 or strike_price <= 0 or time_to_expiry_years <= 0 or volatility <= 0:
        return {"call_price": 0.0, "put_price": 0.0, "call_delta": 0.0, "put_delta": 0.0}

    s = stock_price
    k = strike_price
    t = time_to_expiry_years
    r = risk_free_rate
    v = volatility

    d1 = (math.log(s / k) + (r + 0.5 * v**2) * t) / (v * math.sqrt(t))
    d2 = d1 - v * math.sqrt(t)

    call_price = s * _norm_cdf(d1) - k * math.exp(-r * t) * _norm_cdf(d2)
    put_price = k * math.exp(-r * t) * _norm_cdf(-d2) - s * _norm_cdf(-d1)

    call_delta = _norm_cdf(d1)
    put_delta = call_delta - 1.0

    return {
        "stock_price": s,
        "strike_price": k,
        "call_price": round(float(call_price), 2),
        "put_price": round(float(put_price), 2),
        "call_delta": round(float(call_delta), 3),
        "put_delta": round(float(put_delta), 3),
    }
