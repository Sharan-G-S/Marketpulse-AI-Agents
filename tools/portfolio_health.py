"""
Portfolio Health Score Engine for MarketPulse.

Produces a 0-100 health score for each position and for the overall
portfolio by combining P&L, concentration risk, diversification, and
drawdown metrics.  No LLM required — pure arithmetic.

Scoring dimensions:
    position_health   - P&L performance per holding (0-100)
    concentration_risk - HHI-based single-position overweight penalty
    diversification   - sector/asset spread relative to target weights
    overall_health    - weighted composite of the above (0-100)
"""

# ── Constants ─────────────────────────────────────────────────────────────────

# Score weights for the overall composite (must sum to 1.0)
_WEIGHT_POSITION = 0.40       # average position health
_WEIGHT_CONCENTRATION = 0.30  # concentration risk (inverted)
_WEIGHT_DIVERSIFICATION = 0.30  # diversification health

# P&L return thresholds for position health score
_RETURN_EXCELLENT = 0.20   # +20% → full score
_RETURN_GOOD = 0.05        # +5%  → good score
_RETURN_NEUTRAL = -0.05    # -5%  → neutral boundary
_RETURN_POOR = -0.20       # -20% → poor score


# ── Internal helpers ──────────────────────────────────────────────────────────


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp *value* to the closed interval [*lo*, *hi*]."""
    return max(lo, min(hi, value))


def _safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Return numerator / denominator, or *default* if denominator is zero."""
    return numerator / denominator if denominator != 0.0 else default


# ── Position health ───────────────────────────────────────────────────────────


def compute_position_health_score(
    avg_cost: float,
    current_price: float,
    weight_pct: float = 0.0,
    max_single_weight: float = 0.25,
) -> dict:
    """
    Score an individual portfolio position on a 0-100 scale.

    The score is composed of two components:

    1. **Return score** (70 pts max): Maps the unrealised return onto a
       piecewise linear scale anchored at the thresholds defined in module
       constants (``_RETURN_EXCELLENT``, ``_RETURN_GOOD``, ``_RETURN_NEUTRAL``,
       ``_RETURN_POOR``).

    2. **Weight penalty** (30 pts max): Full marks when the position weight
       is within *max_single_weight*; linearly penalised when over-weight.

    Args:
        avg_cost:          Average cost per share (buy price).
        current_price:     Latest market price per share.
        weight_pct:        Position weight as a decimal fraction (e.g. 0.20
                           for 20 %).  Defaults to 0 (no weight penalty).
        max_single_weight: Maximum acceptable single-position weight before
                           the weight penalty applies.  Defaults to 0.25.

    Returns:
        Dict with keys: ``return_pct``, ``return_score``, ``weight_score``,
        ``total_score``, ``status``.
    """
    if avg_cost <= 0 or current_price <= 0:
        return {
            "return_pct": None,
            "return_score": 0.0,
            "weight_score": 0.0,
            "total_score": 0.0,
            "status": "Error",
        }

    return_pct = _safe_div(current_price - avg_cost, avg_cost)

    # --- Return score (0–70) --------------------------------------------------
    if return_pct >= _RETURN_EXCELLENT:
        return_score = 70.0
    elif return_pct >= _RETURN_GOOD:
        # linear interpolation between GOOD (35 pts) and EXCELLENT (70 pts)
        t = _safe_div(return_pct - _RETURN_GOOD, _RETURN_EXCELLENT - _RETURN_GOOD)
        return_score = 35.0 + t * 35.0
    elif return_pct >= _RETURN_NEUTRAL:
        # linear interpolation between NEUTRAL (20 pts) and GOOD (35 pts)
        t = _safe_div(return_pct - _RETURN_NEUTRAL, _RETURN_GOOD - _RETURN_NEUTRAL)
        return_score = 20.0 + t * 15.0
    elif return_pct >= _RETURN_POOR:
        # linear interpolation between POOR (5 pts) and NEUTRAL (20 pts)
        t = _safe_div(return_pct - _RETURN_POOR, _RETURN_NEUTRAL - _RETURN_POOR)
        return_score = 5.0 + t * 15.0
    else:
        return_score = 0.0

    # --- Weight score (0–30) -------------------------------------------------
    if weight_pct <= max_single_weight:
        weight_score = 30.0
    else:
        # penalise proportionally to over-weight fraction
        over = _safe_div(weight_pct - max_single_weight, max_single_weight)
        weight_score = _clamp(30.0 - over * 30.0, 0.0, 30.0)

    total_score = _clamp(return_score + weight_score)

    # --- Status label --------------------------------------------------------
    if total_score >= 80:
        status = "Excellent"
    elif total_score >= 60:
        status = "Good"
    elif total_score >= 40:
        status = "Neutral"
    elif total_score >= 20:
        status = "Poor"
    else:
        status = "Critical"

    return {
        "return_pct": round(return_pct * 100, 2),
        "return_score": round(return_score, 2),
        "weight_score": round(weight_score, 2),
        "total_score": round(total_score, 2),
        "status": status,
    }


# ── Concentration risk ────────────────────────────────────────────────────────


def compute_portfolio_concentration_risk(
    position_weights: list,
) -> dict:
    """
    Measure single-position concentration risk using the Herfindahl-Hirschman
    Index (HHI).

    HHI = sum(w_i ^ 2) for all position weights w_i in [0, 1].

    Interpretation:
        HHI < 0.15  → Well diversified  (score 100)
        HHI < 0.25  → Acceptable        (score 60-99)
        HHI < 0.40  → Concentrated      (score 20-59)
        HHI >= 0.40 → Highly concentrated (score 0-19)

    Args:
        position_weights: List of decimal weight fractions, e.g. [0.20, 0.30, 0.50].
                          Weights do not need to sum to exactly 1.0 — they are
                          normalised internally.

    Returns:
        Dict with keys: ``hhi``, ``concentration_score`` (0-100),
        ``risk_level``, ``n_positions``.
    """
    weights = [w for w in position_weights if w > 0]
    n = len(weights)
    if n == 0:
        return {
            "hhi": None,
            "concentration_score": 0.0,
            "risk_level": "Error",
            "n_positions": 0,
        }

    total = sum(weights)
    norm = [_safe_div(w, total) for w in weights]
    hhi = round(sum(w ** 2 for w in norm), 6)

    # Map HHI to a 0-100 score (lower HHI = better = higher score)
    if hhi < 0.15:
        concentration_score = 100.0
        risk_level = "Low"
    elif hhi < 0.25:
        # linear: 0.15 → 100, 0.25 → 60
        t = _safe_div(hhi - 0.15, 0.10)
        concentration_score = 100.0 - t * 40.0
        risk_level = "Moderate"
    elif hhi < 0.40:
        # linear: 0.25 → 60, 0.40 → 20
        t = _safe_div(hhi - 0.25, 0.15)
        concentration_score = 60.0 - t * 40.0
        risk_level = "High"
    else:
        # linear: 0.40 → 20, 1.0 → 0
        t = _safe_div(hhi - 0.40, 0.60)
        concentration_score = _clamp(20.0 - t * 20.0)
        risk_level = "Very High"

    return {
        "hhi": hhi,
        "concentration_score": round(concentration_score, 2),
        "risk_level": risk_level,
        "n_positions": n,
    }


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_position_health_score",
    "compute_portfolio_concentration_risk",
]

_MODULE = "tools/portfolio_health"
_VERSION = "2.2.0"
