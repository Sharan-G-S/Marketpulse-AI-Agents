"""
Portfolio Risk Metrics for MarketPulse.

Computes quantitative risk measures from OHLCV price history:
  - Daily / annualised return
  - Volatility (annualised standard deviation of returns)
  - Sharpe Ratio  (risk-adjusted return vs risk-free rate)
  - Sortino Ratio (downside-risk adjusted return)
  - Max Drawdown  (peak-to-trough decline)
  - Value at Risk (95 % historical VaR, 1-day)
  - Calmar Ratio  (annualised return / max drawdown)
  - Beta-adjusted return (vs S&P 500 proxy)

No LLM required — pure statistics.
"""

import math
from typing import Any, Dict, List, Optional

# ── Constants ──────────────────────────────────────────────────────────────

TRADING_DAYS_PER_YEAR = 252
DEFAULT_RISK_FREE_RATE = 0.05  # 5 % annualised (approx US T-bill rate)


# ── Return series ───────────────────────────────────────────────────────────

def compute_daily_returns(price_history: List[Dict[str, Any]]) -> List[float]:
    """
    Compute a list of daily percentage returns from an OHLCV record list.

    Args:
        price_history: List of dicts with at least a ``close`` field,
                       sorted oldest-first.

    Returns:
        List of daily returns as decimals (e.g. 0.012 = +1.2 %).
    """
    closes = [r["close"] for r in price_history if r.get("close") is not None]
    if len(closes) < 2:
        return []
    return [
        (closes[i] - closes[i - 1]) / closes[i - 1] if closes[i - 1] != 0.0 else 0.0
        for i in range(1, len(closes))
    ]


# ── Basic statistics ────────────────────────────────────────────────────────

def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: List[float], ddof: int = 1) -> float:
    if len(values) < 2:
        return 0.0
    mu = _mean(values)
    variance = sum((x - mu) ** 2 for x in values) / (len(values) - ddof)
    return math.sqrt(variance)


def _percentile(values: List[float], pct: float) -> float:
    """Return the *pct*-th percentile of *values* (linear interpolation)."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = (len(sorted_vals) - 1) * pct / 100
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo])


# ── Core risk functions ─────────────────────────────────────────────────────

def annualised_return(daily_returns: List[float]) -> float:
    """Geometric annualised return from daily returns."""
    if not daily_returns:
        return 0.0
    cumulative = 1.0
    for r in daily_returns:
        factor = 1 + r
        if factor <= 0:
            factor = 1e-10  # guard against zero/negative price (degenerate bar)
        cumulative *= factor
    n = len(daily_returns)
    if cumulative <= 0:
        return -1.0
    return cumulative ** (TRADING_DAYS_PER_YEAR / n) - 1


def annualised_volatility(daily_returns: List[float]) -> float:
    """Annualised volatility (std-dev of daily returns × √252)."""
    if len(daily_returns) < 2:
        return 0.0
    return _std(daily_returns) * math.sqrt(TRADING_DAYS_PER_YEAR)


def sharpe_ratio(
    daily_returns: List[float],
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> float:
    """
    Sharpe Ratio = (annualised_return − risk_free_rate) / annualised_volatility.
    Returns 0.0 if volatility is zero.
    """
    vol = annualised_volatility(daily_returns)
    if vol == 0:
        return 0.0
    ar = annualised_return(daily_returns)
    return round((ar - risk_free_rate) / vol, 4)


def sortino_ratio(
    daily_returns: List[float],
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> float:
    """
    Sortino Ratio uses only downside deviation (negative returns) as the
    risk denominator instead of total volatility.
    """
    downside = [r for r in daily_returns if r < 0]
    if len(downside) < 2:
        return 0.0
    downside_std = _std(downside) * math.sqrt(TRADING_DAYS_PER_YEAR)
    if downside_std == 0:
        return 0.0
    ar = annualised_return(daily_returns)
    return round((ar - risk_free_rate) / downside_std, 4)


def max_drawdown(price_history: List[Dict[str, Any]]) -> float:
    """
    Maximum Drawdown = largest peak-to-trough percentage decline.

    Returns a negative decimal, e.g. -0.32 means −32 % drawdown.
    """
    closes = [r["close"] for r in price_history if r.get("close") is not None]
    if len(closes) < 2:
        return 0.0
    peak = closes[0]
    mdd = 0.0
    for c in closes[1:]:
        if c > peak:
            peak = c
        dd = (c - peak) / peak
        if dd < mdd:
            mdd = dd
    return round(mdd, 6)


def value_at_risk_95(daily_returns: List[float]) -> float:
    """
    Historical 95 % Value at Risk (1-day).

    Returns the 5th-percentile daily return as a decimal (negative = loss).
    """
    if not daily_returns:
        return 0.0
    return round(_percentile(daily_returns, 5), 6)


def calmar_ratio(
    daily_returns: List[float],
    price_history: List[Dict[str, Any]],
) -> float:
    """
    Calmar Ratio = annualised_return / abs(max_drawdown).
    Returns 0.0 if max_drawdown is zero.
    """
    mdd = abs(max_drawdown(price_history))
    if mdd == 0:
        return 0.0
    ar = annualised_return(daily_returns)
    return round(ar / mdd, 4)


# ── Risk label ──────────────────────────────────────────────────────────────

def risk_label(sharpe: float, mdd: float, vol: float) -> str:
    """
    Classify overall risk into Low / Moderate / High / Very High based on
    Sharpe, max-drawdown, and annualised volatility.
    """
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


# ── Full metrics bundle ──────────────────────────────────────────────────────

def compute_risk_metrics(
    price_history: List[Dict[str, Any]],
    ticker: str = "",
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> Dict[str, Any]:
    """
    Compute the full risk-metrics bundle for a single ticker.

    Args:
        price_history:  OHLCV record list (oldest first).
        ticker:         Ticker symbol for labelling.
        risk_free_rate: Annual risk-free rate (decimal).

    Returns:
        Dict with keys: ticker, period_days, ann_return, ann_volatility,
        sharpe, sortino, max_drawdown, var_95, calmar, risk_label.
    """
    daily_rets = compute_daily_returns(price_history)
    ar   = round(annualised_return(daily_rets), 6)
    vol  = round(annualised_volatility(daily_rets), 6)
    sh   = sharpe_ratio(daily_rets, risk_free_rate)
    so   = sortino_ratio(daily_rets, risk_free_rate)
    mdd  = max_drawdown(price_history)
    var  = value_at_risk_95(daily_rets)
    cal  = calmar_ratio(daily_rets, price_history)

    return {
        "ticker":         ticker.upper(),
        "period_days":    len(price_history),
        "ann_return":     ar,
        "ann_volatility": vol,
        "sharpe":         sh,
        "sortino":        so,
        "max_drawdown":   mdd,
        "var_95":         var,
        "calmar":         cal,
        "risk_label":     risk_label(sh, mdd, vol),
        "risk_free_rate": risk_free_rate,
    }

# ── Public API ───────────────────────────────────────────────────────────────

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
