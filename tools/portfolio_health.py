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


# ── Diversification health ────────────────────────────────────────────────────


def compute_diversification_health(
    sector_weights: dict,
    target_max_sector: float = 0.30,
) -> dict:
    """
    Score how well the portfolio is spread across sectors.

    A sector that exceeds *target_max_sector* weight is considered
    over-concentrated.  The score penalises both over-concentrated sectors
    and portfolios with fewer than 3 distinct sectors.

    Scoring logic:
        - Start at 100 points.
        - Deduct 15 pts for each sector exceeding the target cap.
        - Deduct 20 pts if fewer than 3 sectors are represented.
        - Deduct 10 pts if fewer than 5 sectors are represented (stacks).

    Args:
        sector_weights:      Dict mapping sector name → decimal weight fraction,
                             e.g. ``{"Tech": 0.40, "Finance": 0.35, "Energy": 0.25}``.
        target_max_sector:   Maximum acceptable weight for any single sector.
                             Defaults to 0.30 (30 %).

    Returns:
        Dict with keys: ``diversification_score`` (0-100), ``n_sectors``,
        ``breached_sectors`` (list), ``assessment``.
    """
    if not sector_weights:
        return {
            "diversification_score": 0.0,
            "n_sectors": 0,
            "breached_sectors": [],
            "assessment": "No sector data",
        }

    total = sum(v for v in sector_weights.values() if v > 0)
    norm = {
        s: _safe_div(w, total)
        for s, w in sector_weights.items()
        if w > 0
    }
    n_sectors = len(norm)
    breached = [s for s, w in norm.items() if w > target_max_sector]

    score = 100.0
    score -= len(breached) * 15.0
    if n_sectors < 3:
        score -= 20.0
    if n_sectors < 5:
        score -= 10.0

    score = _clamp(score)

    if score >= 80:
        assessment = "Well Diversified"
    elif score >= 55:
        assessment = "Adequately Diversified"
    elif score >= 30:
        assessment = "Needs Improvement"
    else:
        assessment = "Poorly Diversified"

    return {
        "diversification_score": round(score, 2),
        "n_sectors": n_sectors,
        "breached_sectors": breached,
        "assessment": assessment,
    }


# ── Public API ────────────────────────────────────────────────────────────────

# ── Grade classifier ─────────────────────────────────────────────────────────


def health_grade(score: float) -> str:
    """
    Convert a numeric health score (0-100) into a letter grade.

    Grade bands:
        A+ : 95 – 100  (Exceptional)
        A  : 85 – 94   (Excellent)
        B  : 70 – 84   (Good)
        C  : 55 – 69   (Neutral / Watch)
        D  : 35 – 54   (Poor)
        F  :  0 – 34   (Critical)

    Args:
        score: Numeric score in [0, 100].

    Returns:
        Letter grade string: 'A+', 'A', 'B', 'C', 'D', or 'F'.
    """
    s = _clamp(score)
    if s >= 95:
        return "A+"
    if s >= 85:
        return "A"
    if s >= 70:
        return "B"
    if s >= 55:
        return "C"
    if s >= 35:
        return "D"
    return "F"


# ── Overall portfolio health ──────────────────────────────────────────────────


def compute_overall_portfolio_health(
    positions: list,
    sector_weights: dict,
    snapshots: dict,
) -> dict:
    """
    Compute a composite portfolio health score from all sub-dimensions.

    The composite is a weighted average of:
        - Average position health score  (weight: 40 %)
        - Concentration score            (weight: 30 %)
        - Diversification score          (weight: 30 %)

    Args:
        positions:      List of position dicts, each containing:
                        ``ticker`` (str), ``qty`` (float), ``avg_cost`` (float).
        sector_weights: Dict mapping sector name → decimal weight fraction.
        snapshots:      Dict mapping ticker → current market price (float).

    Returns:
        Dict with keys: ``overall_score``, ``grade``, ``position_avg_score``,
        ``concentration``, ``diversification``, ``position_scores`` (list).
    """
    if not positions or not snapshots:
        return {
            "overall_score": 0.0,
            "grade": "F",
            "position_avg_score": 0.0,
            "concentration": {},
            "diversification": {},
            "position_scores": [],
        }

    # Compute each position weight by market value
    mv_map = {}
    for pos in positions:
        ticker = pos.get("ticker", "")
        qty = pos.get("qty", 0.0)
        price = snapshots.get(ticker, 0.0)
        mv_map[ticker] = qty * price

    total_mv = sum(mv_map.values())

    # Score individual positions
    position_scores = []
    for pos in positions:
        ticker = pos.get("ticker", "")
        avg_cost = pos.get("avg_cost", 0.0)
        current_price = snapshots.get(ticker, 0.0)
        weight = _safe_div(mv_map.get(ticker, 0.0), total_mv)
        phs = compute_position_health_score(avg_cost, current_price, weight)
        position_scores.append({
            "ticker": ticker,
            **phs,
        })

    avg_position_score = _safe_div(
        sum(p["total_score"] for p in position_scores),
        len(position_scores),
    )

    # Concentration risk
    weights_list = [_safe_div(mv_map.get(p.get("ticker", ""), 0.0), total_mv)
                    for p in positions]
    concentration = compute_portfolio_concentration_risk(weights_list)

    # Diversification health
    diversification = compute_diversification_health(sector_weights)

    # Composite score
    overall_score = _clamp(
        avg_position_score * _WEIGHT_POSITION
        + concentration["concentration_score"] * _WEIGHT_CONCENTRATION
        + diversification["diversification_score"] * _WEIGHT_DIVERSIFICATION
    )

    return {
        "overall_score": round(overall_score, 2),
        "grade": health_grade(overall_score),
        "position_avg_score": round(avg_position_score, 2),
        "concentration": concentration,
        "diversification": diversification,
        "position_scores": position_scores,
    }


# ── Markdown report ───────────────────────────────────────────────────────────


def format_health_report(health: dict, portfolio_name: str = "Portfolio") -> str:
    """
    Render a full portfolio health report as a Markdown string.

    Args:
        health:         Output of ``compute_overall_portfolio_health()``.
        portfolio_name: Display name for the report heading.

    Returns:
        Multi-section Markdown string with overall score, grade, concentration
        risk, diversification, and a per-position breakdown table.
    """
    score = health.get("overall_score", 0.0)
    grade = health.get("grade", "F")
    pos_avg = health.get("position_avg_score", 0.0)
    concentration = health.get("concentration", {})
    diversification = health.get("diversification", {})
    position_scores = health.get("position_scores", [])

    grade_emoji = {
        "A+": "🌟", "A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"
    }.get(grade, "⚪")

    bar_filled = int(score / 10)
    score_bar = "█" * bar_filled + "░" * (10 - bar_filled)

    lines = [
        f"## 🏥 {portfolio_name} — Health Report",
        "",
        f"**Overall Score:** {score:.1f}/100  [{score_bar}]",
        f"**Grade:** {grade_emoji} {grade}  |  **Avg Position Score:** {pos_avg:.1f}",
        "",
        "---",
        "",
        "### 🎯 Concentration Risk",
        f"- **HHI:** {concentration.get('hhi', 'N/A')}",
        f"- **Risk Level:** {concentration.get('risk_level', 'N/A')}",
        f"- **Concentration Score:** {concentration.get('concentration_score', 0):.1f}/100",
        f"- **Positions:** {concentration.get('n_positions', 0)}",
        "",
        "### 🌐 Diversification Health",
        f"- **Assessment:** {diversification.get('assessment', 'N/A')}",
        f"- **Diversification Score:** {diversification.get('diversification_score', 0):.1f}/100",
        f"- **Sectors:** {diversification.get('n_sectors', 0)}",
    ]

    breached = diversification.get("breached_sectors", [])
    if breached:
        lines.append(f"- **Over-weight Sectors:** {', '.join(breached)}")

    lines += [
        "",
        "### 📊 Position Breakdown",
        "",
        "| Ticker | Return % | Score | Grade | Status |",
        "|--------|----------|-------|-------|--------|",
    ]

    for ps in position_scores:
        ticker = ps.get("ticker", "?")
        ret = ps.get("return_pct")
        ret_str = f"{ret:+.2f}%" if ret is not None else "N/A"
        ts = ps.get("total_score", 0.0)
        g = health_grade(ts)
        status = ps.get("status", "N/A")
        g_emoji = {
            "A+": "🌟", "A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"
        }.get(g, "⚪")
        lines.append(f"| {ticker} | {ret_str} | {ts:.1f} | {g_emoji} {g} | {status} |")

    return "\n".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_position_health_score",
    "compute_portfolio_concentration_risk",
    "compute_diversification_health",
    "health_grade",
    "compute_overall_portfolio_health",
    "format_health_report",
]

_MODULE = "tools/portfolio_health"
_VERSION = "2.2.0"
