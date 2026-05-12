"""
Portfolio Diversification Scorer for MarketPulse.

Computes a 0–100 composite diversification score for a portfolio
based on three dimensions:
  1. Sector spread  — how evenly weight is distributed across sectors
  2. Ticker concentration — Herfindahl-Hirschman Index (HHI) of weights
  3. Position count — rewarded up to a cap of ~20 positions

No LLM required — pure arithmetic (no external imports beyond math).
"""

import math
from typing import Any, Dict, List, Optional, Tuple

# ── Type aliases ──────────────────────────────────────────────────────────────

DiversificationResult = Dict[str, Any]
"""
{
    "score":              float,   # 0-100 composite score
    "grade":              str,     # A / B / C / D / F
    "sector_score":       float,   # 0-100 sector-spread sub-score
    "concentration_score":float,   # 0-100 HHI-based sub-score
    "count_score":        float,   # 0-100 position-count sub-score
    "hhi":                float,   # Herfindahl-Hirschman Index (0-1)
    "n_sectors":          int,
    "n_positions":        int,
    "dominant_sector":    str,
    "dominant_weight_pct":float,
    "interpretation":     str,
    "suggestions":        List[str],
}
"""


# ── Herfindahl-Hirschman Index ────────────────────────────────────────────────

def compute_hhi(weights: List[float]) -> float:
    """
    Compute the Herfindahl-Hirschman Index from a list of portfolio weights.

    Args:
        weights: List of weight fractions (should sum to ~1.0).

    Returns:
        HHI value in [0, 1].  Higher = more concentrated.
    """
    if not weights:
        return 1.0
    total = sum(weights)
    if total == 0:
        return 1.0
    norm = [w / total for w in weights]
    return round(sum(w ** 2 for w in norm), 6)


# ── Sector entropy ────────────────────────────────────────────────────────────

def sector_entropy(sector_weights: Dict[str, float]) -> float:
    """
    Compute normalised Shannon entropy for sector allocation.

    Args:
        sector_weights: Dict mapping sector → total market value.

    Returns:
        Normalised entropy in [0, 1].  1.0 = perfectly even distribution.
    """
    if not sector_weights:
        return 0.0
    total = sum(sector_weights.values())
    if total == 0 or len(sector_weights) == 1:
        return 0.0

    max_entropy = math.log(len(sector_weights))
    entropy = -sum(
        (v / total) * math.log(v / total)
        for v in sector_weights.values()
        if v > 0
    )
    return round(entropy / max_entropy, 6) if max_entropy > 0 else 0.0


# ── Sub-scores ────────────────────────────────────────────────────────────────

def _sector_score(entropy: float) -> float:
    """Map normalised entropy [0, 1] to a 0-100 sector score."""
    return round(entropy * 100, 2)


def _concentration_score(hhi: float) -> float:
    """
    Map HHI to a 0-100 score where lower HHI = higher score.

    HHI = 1/N for a perfectly equal N-stock portfolio.
    Score is 100 when HHI approaches 0, and 0 when HHI = 1 (one stock).
    """
    return round(max(0.0, (1.0 - hhi) * 100), 2)


def _count_score(n: int, cap: int = 20) -> float:
    """
    Map position count to 0-100 score, capped at *cap* positions = 100.
    Uses square-root scaling so early diversification is heavily rewarded.
    """
    if n <= 0:
        return 0.0
    return round(min(100.0, (math.sqrt(n) / math.sqrt(cap)) * 100), 2)


# ── Grade mapping ─────────────────────────────────────────────────────────────

def _grade(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    if score >= 35:
        return "D"
    return "F"


# ── Suggestions engine ────────────────────────────────────────────────────────

def _suggestions(
    n_positions: int,
    n_sectors: int,
    dominant_pct: float,
    hhi: float,
    grade: str,
) -> List[str]:
    tips: List[str] = []
    if n_positions < 5:
        tips.append("Add more positions — a minimum of 8-10 stocks is recommended.")
    if n_sectors < 3:
        tips.append("Spread across at least 3-4 sectors to reduce sector-specific risk.")
    if dominant_pct > 40:
        tips.append(
            f"Your largest sector is {dominant_pct:.1f}% of the portfolio — "
            "consider trimming to below 35%."
        )
    if hhi > 0.25:
        tips.append("HHI > 0.25 indicates high concentration — rebalance top positions.")
    if grade == "A":
        tips.append("Portfolio is well-diversified — maintain current allocation balance.")
    return tips


# ── Main entry point ──────────────────────────────────────────────────────────

def score_diversification(
    positions: List[Dict[str, Any]],
    sector_map: Optional[Dict[str, str]] = None,
    weights: Optional[List[float]] = None,
    sector_weights: Optional[Dict[str, float]] = None,
) -> DiversificationResult:
    """
    Compute a composite diversification score for a portfolio.

    Args:
        positions:      List of position dicts with at least 'ticker' key.
                        Optionally 'market_value' for weight computation.
        sector_map:     Dict mapping ticker → sector name. Unknown → 'Other'.
        weights:        Pre-computed portfolio weight fractions (optional).
                        If omitted, computed from positions['market_value'].
        sector_weights: Pre-computed sector → market value dict (optional).
                        If omitted, computed from positions + sector_map.

    Returns:
        DiversificationResult dict with composite score, grade, sub-scores,
        HHI, sector stats, and actionable suggestions.
    """
    sm = sector_map or {}
    n  = len(positions)

    # Compute weights from market_value if not provided
    if weights is None:
        mvs = [float(p.get("market_value", 1.0)) for p in positions]
        total_mv = sum(mvs) or 1.0
        weights = [mv / total_mv for mv in mvs]

    # Compute sector_weights if not provided
    if sector_weights is None:
        sw: Dict[str, float] = {}
        for p, w in zip(positions, weights):
            sector = sm.get(str(p.get("ticker", "")).upper(), "Other")
            sw[sector] = sw.get(sector, 0.0) + w
        sector_weights = sw

    # Scores
    hhi        = compute_hhi(weights)
    entropy    = sector_entropy(sector_weights)
    sec_score  = _sector_score(entropy)
    conc_score = _concentration_score(hhi)
    cnt_score  = _count_score(n)

    # Composite (weighted average)
    composite = round(0.40 * sec_score + 0.40 * conc_score + 0.20 * cnt_score, 2)
    grade     = _grade(composite)

    # Dominant sector
    dominant_sector = max(sector_weights, key=sector_weights.get) if sector_weights else "Unknown"  # type: ignore
    dominant_pct    = round(sector_weights.get(dominant_sector, 0.0) * 100, 2)

    n_sectors = len(sector_weights)
    tips      = _suggestions(n, n_sectors, dominant_pct, hhi, grade)

    interp_map = {
        "A": "Well-diversified — excellent spread across sectors and positions.",
        "B": "Good diversification — minor concentration risk; consider small tweaks.",
        "C": "Moderate diversification — notable concentration; review sector balance.",
        "D": "Poor diversification — high concentration risk; rebalancing recommended.",
        "F": "Very poorly diversified — heavily concentrated in one or few positions.",
    }

    return {
        "score":               composite,
        "grade":               grade,
        "sector_score":        sec_score,
        "concentration_score": conc_score,
        "count_score":         cnt_score,
        "hhi":                 hhi,
        "n_sectors":           n_sectors,
        "n_positions":         n,
        "dominant_sector":     dominant_sector,
        "dominant_weight_pct": dominant_pct,
        "interpretation":      interp_map.get(grade, ""),
        "suggestions":         tips,
    }


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_hhi",
    "sector_entropy",
    "score_diversification",
]

_MODULE = "tools/diversification_scorer.py"
_VERSION = "1.7.0"
