"""
Stock Comparison Agent for MarketPulse.

Compares two or more stock tickers side-by-side across fundamental data,
technical indicators, and a composite scoring model — all without an LLM call.

Produces a structured ComparisonResult that can be rendered as a Markdown
table or consumed by the Streamlit Compare Stocks page.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

TickerData = Dict[str, Any]
"""
Per-ticker data bundle expected by the comparison agent:
    {
        "ticker":         str,
        "company_name":   str,         (optional)
        "current_price":  float,
        "change_pct":     float,
        "market_cap":     float,
        "pe_ratio":       float | None,
        "beta":           float | None,
        "52w_high":       float | None,
        "52w_low":        float | None,
        "sector":         str,
        "rsi":            float | None,
        "macd":           dict | None,  (keys: macd, signal, crossover)
        "sma_20":         float | None,
        "sma_50":         float | None,
        "ma_signal":      str | None,
    }
"""

ComparisonResult = Dict[str, Any]


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

_MAX_SCORE = 100.0
_SCORE_COMPONENTS = {
    "momentum":    0.25,   # recent price change
    "valuation":   0.20,   # PE ratio (lower = better)
    "technical":   0.25,   # RSI + MACD crossover + MA signal
    "stability":   0.15,   # beta (lower = more stable)
    "52w_range":   0.15,   # price position within 52-week range
}


def _score_momentum(change_pct: float) -> float:
    """Map daily % change → 0–100. ±10 % extremes map to 0 / 100."""
    clipped = max(-10.0, min(10.0, change_pct))
    return round((clipped + 10.0) / 20.0 * 100.0, 1)


def _score_valuation(pe: Optional[float]) -> float:
    """Map PE ratio → 0–100.  PE ≤10 → 100; PE ≥60 → 0; None → 50."""
    if pe is None or pe <= 0:
        return 50.0
    if pe <= 10:
        return 100.0
    if pe >= 60:
        return 0.0
    # Linear interpolation between 10 and 60
    return round((60.0 - pe) / 50.0 * 100.0, 1)


def _score_technical(
    rsi: Optional[float],
    macd: Optional[Dict[str, Any]],
    ma_signal: Optional[str],
) -> float:
    """Combine RSI, MACD crossover and MA signal into a 0–100 score."""
    points = 0.0
    weight_total = 0.0

    # RSI — optimal around 50; extremes penalised
    if rsi is not None:
        dist_from_neutral = abs(rsi - 50.0)
        rsi_score = max(0.0, 100.0 - dist_from_neutral * 2.0)
        points += rsi_score * 0.4
        weight_total += 0.4

    # MACD crossover
    if macd:
        crossover = macd.get("crossover", "")
        if crossover == "Bullish":
            points += 100.0 * 0.35
        else:
            points += 0.0 * 0.35
        weight_total += 0.35

    # MA signal
    if ma_signal:
        if "Golden" in ma_signal:
            points += 100.0 * 0.25
        elif "Death" in ma_signal:
            points += 0.0 * 0.25
        else:
            points += 50.0 * 0.25
        weight_total += 0.25

    if weight_total == 0:
        return 50.0
    return round(points / weight_total, 1)


def _score_stability(beta: Optional[float]) -> float:
    """Map beta → stability score 0–100.  Beta=1 → 70; lower is better."""
    if beta is None:
        return 50.0
    if beta <= 0.5:
        return 100.0
    if beta >= 2.5:
        return 0.0
    # Linear from 0.5→100 to 2.5→0
    return round((2.5 - beta) / 2.0 * 100.0, 1)


def _score_52w_range(
    current: float,
    high: Optional[float],
    low: Optional[float],
) -> float:
    """Position within 52-week range → 0–100 (higher = closer to 52w high)."""
    if high is None or low is None or high == low:
        return 50.0
    position = (current - low) / (high - low)
    return round(max(0.0, min(1.0, position)) * 100.0, 1)


def compute_composite_score(ticker_data: TickerData) -> float:
    """
    Compute a weighted composite score (0–100) for a single ticker.

    Higher score = stronger buy signal across all dimensions.
    """
    w = _SCORE_COMPONENTS

    s_momentum = _score_momentum(ticker_data.get("change_pct", 0.0))
    s_valuation = _score_valuation(ticker_data.get("pe_ratio"))
    s_technical = _score_technical(
        ticker_data.get("rsi"),
        ticker_data.get("macd"),
        ticker_data.get("ma_signal"),
    )
    s_stability = _score_stability(ticker_data.get("beta"))
    s_range = _score_52w_range(
        ticker_data.get("current_price", 0.0),
        ticker_data.get("52w_high"),
        ticker_data.get("52w_low"),
    )

    composite = (
        s_momentum  * w["momentum"]
        + s_valuation * w["valuation"]
        + s_technical * w["technical"]
        + s_stability * w["stability"]
        + s_range     * w["52w_range"]
    )
    return round(composite, 1)


def score_label(score: float) -> str:
    """Return a human-readable label for a composite score."""
    if score >= 75:
        return "Strong Buy"
    if score >= 60:
        return "Buy"
    if score >= 45:
        return "Hold"
    if score >= 30:
        return "Sell"
    return "Strong Sell"


# ---------------------------------------------------------------------------
# Comparison agent
# ---------------------------------------------------------------------------

def compare_tickers(
    tickers_data: List[TickerData],
) -> ComparisonResult:
    """
    Perform a side-by-side comparison of multiple tickers.

    Args:
        tickers_data: List of TickerData dicts (minimum 2 tickers).

    Returns:
        ComparisonResult with:
            - tickers:       list of ticker symbols
            - scores:        dict ticker → composite score
            - rankings:      list sorted best → worst
            - winner:        ticker with highest composite score
            - breakdown:     per-ticker score breakdown
            - generated_at:  ISO-8601 UTC timestamp
    """
    if not tickers_data:
        return {
            "error": "No ticker data provided.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    scores: Dict[str, float] = {}
    breakdown: Dict[str, Dict[str, float]] = {}

    for td in tickers_data:
        t = td.get("ticker", "UNKNOWN").upper()
        w = _SCORE_COMPONENTS

        s_mom = _score_momentum(td.get("change_pct", 0.0))
        s_val = _score_valuation(td.get("pe_ratio"))
        s_tec = _score_technical(td.get("rsi"), td.get("macd"), td.get("ma_signal"))
        s_sta = _score_stability(td.get("beta"))
        s_rng = _score_52w_range(
            td.get("current_price", 0.0),
            td.get("52w_high"),
            td.get("52w_low"),
        )

        composite = round(
            s_mom * w["momentum"]
            + s_val * w["valuation"]
            + s_tec * w["technical"]
            + s_sta * w["stability"]
            + s_rng * w["52w_range"],
            1,
        )
        scores[t] = composite
        breakdown[t] = {
            "momentum_score":  s_mom,
            "valuation_score": s_val,
            "technical_score": s_tec,
            "stability_score": s_sta,
            "range_score":     s_rng,
            "composite":       composite,
            "label":           score_label(composite),
        }

    # Rankings
    rankings = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner = rankings[0][0] if rankings else None

    return {
        "tickers": [td.get("ticker", "?").upper() for td in tickers_data],
        "scores": scores,
        "rankings": [{"ticker": t, "score": s, "label": score_label(s)} for t, s in rankings],
        "winner": winner,
        "breakdown": breakdown,
        "raw": {td.get("ticker", "?").upper(): td for td in tickers_data},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
