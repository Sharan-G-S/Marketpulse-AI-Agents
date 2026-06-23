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


# ── Public API ────────────────────────────────────────────────────────────────

__all__: list = []

_MODULE = "tools/portfolio_health"
_VERSION = "2.2.0"
