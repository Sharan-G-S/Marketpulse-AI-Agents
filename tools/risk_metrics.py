"""
Portfolio Risk Metrics for MarketPulse with ZeroDivision Guards.
"""

import math
from typing import Any, Dict, List

TRADING_DAYS_PER_YEAR = 252
DEFAULT_RISK_FREE_RATE = 0.05


def compute_daily_returns(price_history: List[Dict[str, Any]]) -> List[float]:
    closes = [r["close"] for r in price_history if isinstance(r, dict) and r.get("close") is not None]
    if len(closes) < 2:
        return []
    return [
        (closes[i] - closes[i - 1]) / closes[i - 1] if closes[i - 1] != 0.0 else 0.0
        for i in range(1, len(closes))
    ]


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: List[float], ddof: int = 1) -> float:
    if len(values) < 2:
        return 0.0
    mu = _mean(values)
    variance = sum((x - mu) ** 2 for x in values) / max(1, (len(values) - ddof))
    return math.sqrt(variance)


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = (len(sorted_vals) - 1) * pct / 100
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo])


def annualised_return(daily_returns: List[float]) -> float:
    if not daily_returns:
        return 0.0
    cumulative = 1.0
    for r in daily_returns:
        factor = 1 + r
        if factor <= 0:
            factor = 1e-10
        cumulative *= factor
    n = len(daily_returns)
    if cumulative <= 0 or n == 0:
        return -1.0
    return cumulative ** (TRADING_DAYS_PER_YEAR / n) - 1


def annualised_volatility(daily_returns: List[float]) -> float:
    if len(daily_returns) < 2:
        return 0.0
    return _std(daily_returns) * math.sqrt(TRADING_DAYS_PER_YEAR)


def sharpe_ratio(
    daily_returns: List[float],
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> float:
    if not daily_returns:
        return 0.0
    vol = annualised_volatility(daily_returns)
    if vol == 0.0 or math.isnan(vol):
        return 0.0
    ar = annualised_return(daily_returns)
    return round((ar - risk_free_rate) / vol, 4)


def sortino_ratio(
    daily_returns: List[float],
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> float:
    if not daily_returns:
        return 0.0
    downside = [r for r in daily_returns if r < 0]
    if len(downside) < 2:
        return 0.0
    downside_std = _std(downside) * math.sqrt(TRADING_DAYS_PER_YEAR)
    if downside_std == 0.0 or math.isnan(downside_std):
        return 0.0
    ar = annualised_return(daily_returns)
    return round((ar - risk_free_rate) / downside_std, 4)


def max_drawdown(price_history: List[Dict[str, Any]]) -> float:
    closes = [r["close"] for r in price_history if isinstance(r, dict) and r.get("close") is not None]
    if len(closes) < 2:
        return 0.0
    peak = closes[0]
    mdd = 0.0
    for c in closes[1:]:
        if c > peak:
            peak = c
        if peak == 0:
            continue
        dd = (c - peak) / peak
        if dd < mdd:
            mdd = dd
    return round(mdd, 6)


def value_at_risk_95(daily_returns: List[float]) -> float:
    if not daily_returns:
        return 0.0
    return round(_percentile(daily_returns, 5), 6)


def calmar_ratio(
    daily_returns: List[float],
    price_history: List[Dict[str, Any]],
) -> float:
    mdd = abs(max_drawdown(price_history))
    if mdd == 0:
        return 0.0
    ar = annualised_return(daily_returns)
    return round(ar / mdd, 4)


def risk_label(sharpe: float, mdd: float, vol: float) -> str:
    score = 0
    if sharpe < 0:
        score += 3
    elif sharpe < 0.5:
        score += 2
    elif sharpe < 1.0:
        score += 1

    if mdd < -0.30:
        score += 3
    elif mdd < -0.15:
        score += 2
    elif mdd < -0.05:
        score += 1

    if vol > 0.50:
        score += 3
    elif vol > 0.30:
        score += 2
    elif vol > 0.15:
        score += 1

    if score >= 7:
        return "Very High"
    if score >= 4:
        return "High"
    if score >= 2:
        return "Moderate"
    return "Low"


def compute_risk_metrics(
    price_history: List[Dict[str, Any]],
    ticker: str = "",
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> Dict[str, Any]:
    daily_rets = compute_daily_returns(price_history)
    ar = round(annualised_return(daily_rets), 6)
    vol = round(annualised_volatility(daily_rets), 6)
    sh = sharpe_ratio(daily_rets, risk_free_rate)
    so = sortino_ratio(daily_rets, risk_free_rate)
    mdd = max_drawdown(price_history)
    var = value_at_risk_95(daily_rets)
    cal = calmar_ratio(daily_rets, price_history)

    return {
        "ticker": ticker.upper() if ticker else "",
        "period_days": len(price_history),
        "ann_return": ar,
        "ann_volatility": vol,
        "sharpe": sh,
        "sortino": so,
        "max_drawdown": mdd,
        "var_95": var,
        "calmar": cal,
        "risk_label": risk_label(sh, mdd, vol),
        "risk_free_rate": risk_free_rate,
    }


__all__ = [
    "TRADING_DAYS_PER_YEAR",
    "DEFAULT_RISK_FREE_RATE",
    "compute_daily_returns",
    "annualised_return",
    "annualised_volatility",
    "sharpe_ratio",
    "sortino_ratio",
    "max_drawdown",
    "value_at_risk_95",
    "calmar_ratio",
    "risk_label",
    "compute_risk_metrics",
]
