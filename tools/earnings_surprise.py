"""
Earnings Surprise Tracker for MarketPulse.

Computes earnings surprise magnitude and direction by comparing
reported EPS against analyst consensus estimates, then classifies
the result into beat/miss/meet tiers with a % surprise score.

No LLM required — pure arithmetic.
"""

from typing import Any, Dict, List, Optional, Tuple

# ── Type aliases ──────────────────────────────────────────────────────────────

EarningsRecord = Dict[str, Any]
"""
{
    "ticker":       str,
    "period":       str,    # e.g. "Q1 2026"
    "reported_eps": float,
    "estimated_eps":float,
    "revenue_actual":    float | None,
    "revenue_estimate":  float | None,
    "report_date":  str | None,   # YYYY-MM-DD
}
"""

SurpriseResult = Dict[str, Any]
"""
{
    "ticker":           str,
    "period":           str,
    "reported_eps":     float,
    "estimated_eps":    float,
    "eps_surprise_pct": float,   # (reported - estimated) / |estimated| * 100
    "eps_surprise_abs": float,
    "eps_verdict":      str,     # "Strong Beat" | "Beat" | "Meet" | "Miss" | "Strong Miss"
    "revenue_surprise_pct": float | None,
    "revenue_verdict":  str | None,
    "overall_verdict":  str,
    "report_date":      str | None,
}
"""


# ── Thresholds ────────────────────────────────────────────────────────────────

SURPRISE_THRESHOLDS = {
    "strong_beat":  5.0,   # ≥ +5% surprise = Strong Beat
    "beat":         1.0,   # ≥ +1% surprise = Beat
    "meet":        -1.0,   # ≥ -1% surprise = Meet (within ±1%)
    "miss":        -5.0,   # ≥ -5% surprise = Miss
    # < -5% = Strong Miss
}


# ── Core computation ──────────────────────────────────────────────────────────

def compute_eps_surprise(
    reported: float,
    estimated: float,
) -> Tuple[float, float]:
    """
    Compute EPS surprise percentage and absolute delta.

    Args:
        reported:  Actual reported EPS.
        estimated: Analyst consensus EPS estimate.
                   May be negative (loss-making companies) — abs() is used
                   in the denominator so direction is preserved correctly.

    Returns:
        (surprise_pct, surprise_abs) tuple.
        surprise_pct = (reported - estimated) / |estimated| * 100
        Returns (0.0, abs_delta) if estimated is 0 to avoid division by zero.

    Examples:
        >>> compute_eps_surprise(2.20, 2.00)   # +10% beat
        (10.0, 0.2)
        >>> compute_eps_surprise(-0.10, -0.20) # beat on loss: reported -0.10 vs est -0.20
        (50.0, 0.1)
    """
    surprise_abs = round(reported - estimated, 4)
    if estimated == 0:
        return (0.0, surprise_abs)
    surprise_pct = round((reported - estimated) / abs(estimated) * 100, 4)
    return (surprise_pct, surprise_abs)


def eps_verdict(surprise_pct: float) -> str:
    """Classify an EPS surprise percentage into a verdict tier."""
    t = SURPRISE_THRESHOLDS
    if surprise_pct >= t["strong_beat"]:
        return "Strong Beat 🚀"
    if surprise_pct >= t["beat"]:
        return "Beat 🟢"
    if surprise_pct >= t["meet"]:
        return "Meet ⚪"
    if surprise_pct >= t["miss"]:
        return "Miss 🟡"
    return "Strong Miss 🔴"


def revenue_verdict(surprise_pct: Optional[float]) -> Optional[str]:
    """Classify a revenue surprise percentage. Returns None if no data."""
    if surprise_pct is None:
        return None
    if surprise_pct >= 3.0:
        return "Revenue Beat 🟢"
    if surprise_pct >= -1.0:
        return "Revenue In-Line ⚪"
    return "Revenue Miss 🔴"


def overall_verdict(eps_v: str, rev_v: Optional[str]) -> str:
    """Derive a single overall verdict from EPS + revenue verdicts."""
    if "Strong Beat" in eps_v:
        return "Outstanding 🌟" if rev_v and "Beat" in rev_v else "Strong Beat 🚀"
    if "Beat" in eps_v:
        return "Positive 🟢" if not rev_v or "Miss" not in rev_v else "Mixed 🟡"
    if "Strong Miss" in eps_v:
        return "Disappointing 🔴"
    if "Miss" in eps_v:
        return "Negative 🟡"
    return "Neutral ⚪"


def compute_earnings_surprise(record: EarningsRecord) -> SurpriseResult:
    """
    Compute the full earnings surprise result for a single EarningsRecord.

    Args:
        record: EarningsRecord dict with ticker, period, reported/estimated EPS.

    Returns:
        SurpriseResult dict with all computed fields.
    """
    ticker    = str(record.get("ticker", "")).upper()
    period    = str(record.get("period", ""))
    try:
        reported = float(record.get("reported_eps", 0.0) or 0.0)
    except (ValueError, TypeError):
        reported = 0.0

    try:
        estimated = float(record.get("estimated_eps", 0.0) or 0.0)
    except (ValueError, TypeError):
        estimated = 0.0

    eps_pct, eps_abs = compute_eps_surprise(reported, estimated)
    eps_v = eps_verdict(eps_pct)

    # Revenue surprise (optional)
    rev_actual = record.get("revenue_actual")
    rev_estimate = record.get("revenue_estimate")
    rev_pct: Optional[float] = None
    if rev_actual is not None and rev_estimate is not None:
        try:
            act_val = float(rev_actual)
            est_val = float(rev_estimate)
            if est_val != 0:
                rev_pct = round((act_val - est_val) / abs(est_val) * 100, 4)
        except (ValueError, TypeError):
            pass
    rev_v = revenue_verdict(rev_pct)

    return {
        "ticker":               ticker,
        "period":               period,
        "reported_eps":         reported,
        "estimated_eps":        estimated,
        "eps_surprise_pct":     eps_pct,
        "eps_surprise_abs":     eps_abs,
        "eps_verdict":          eps_v,
        "revenue_surprise_pct": rev_pct,
        "revenue_verdict":      rev_v,
        "overall_verdict":      overall_verdict(eps_v, rev_v),
        "report_date":          record.get("report_date"),
    }


def compute_earnings_history(records: List[EarningsRecord]) -> List[SurpriseResult]:
    """
    Compute earnings surprises for a list of records.

    Returns:
        List of SurpriseResult dicts, preserving input order.
    """
    return [compute_earnings_surprise(r) for r in records]


def earnings_trend(results: List[SurpriseResult]) -> Dict[str, Any]:
    """
    Summarise the earnings surprise trend across multiple periods.

    Args:
        results: List of SurpriseResult dicts (chronological order recommended).

    Returns:
        Dict with beat_count, miss_count, avg_surprise_pct, trend_label.
    """
    if not results:
        return {"beat_count": 0, "miss_count": 0, "avg_surprise_pct": 0.0, "trend_label": "N/A"}

    beats  = sum(1 for r in results if r["eps_surprise_pct"] >= SURPRISE_THRESHOLDS["beat"])
    misses = sum(1 for r in results if r["eps_surprise_pct"] < SURPRISE_THRESHOLDS["meet"])
    avg    = round(sum(r["eps_surprise_pct"] for r in results) / len(results), 4)

    if beats >= len(results) * 0.75:
        label = "Consistent Beater 🌟"
    elif beats > misses:
        label = "More Beats than Misses 🟢"
    elif misses > beats:
        label = "More Misses than Beats 🔴"
    else:
        label = "Mixed Track Record ⚪"

    return {
        "beat_count":       beats,
        "miss_count":       misses,
        "avg_surprise_pct": avg,
        "trend_label":      label,
        "n_periods":        len(results),
    }


def format_earnings_table(results: List[SurpriseResult]) -> str:
    """Render earnings surprise results as a Markdown table."""
    if not results:
        return "_No earnings data available._"

    ticker = results[0]["ticker"] if results else ""
    lines = [
        f"### 📊 Earnings Surprise History — {ticker}\n",
        "| Period | Reported EPS | Est. EPS | Surprise % | Verdict |",
        "|--------|-------------|---------|------------|---------|",
    ]
    for r in results:
        lines.append(
            f"| {r['period']} "
            f"| ${r['reported_eps']:.2f} "
            f"| ${r['estimated_eps']:.2f} "
            f"| {r['eps_surprise_pct']:+.2f}% "
            f"| {r['eps_verdict']} |"
        )
    return "\n".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "SURPRISE_THRESHOLDS",
    "compute_eps_surprise",
    "eps_verdict",
    "revenue_verdict",
    "overall_verdict",
    "compute_earnings_surprise",
    "compute_earnings_history",
    "earnings_trend",
    "format_earnings_table",
]

_MODULE = "tools/earnings_surprise.py"
_VERSION = "1.7.0"
