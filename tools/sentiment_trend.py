"""
News Sentiment Trend Utility for MarketPulse.

Aggregates per-article sentiment scores across multiple analysis runs
(or simulated time windows) to produce a daily sentiment trend that can
be plotted on a Streamlit line chart.

No LLM calls — pure aggregation of already-computed sentiment_scores.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

SentimentRecord = Dict[str, Any]
"""
A single article's sentiment entry (from state['sentiment_scores']):
    {
        "title":     str,
        "sentiment": "Bullish" | "Bearish" | "Neutral",
        "score":     float,     # -1.0 to +1.0
        "date":      str,       # ISO date string YYYY-MM-DD (optional)
    }
"""

TrendPoint = Dict[str, Any]
"""
Aggregated sentiment for one time window:
    {
        "date":          str,       # YYYY-MM-DD
        "avg_score":     float,     # mean score (-1 to +1)
        "bullish_count": int,
        "bearish_count": int,
        "neutral_count": int,
        "total":         int,
        "label":         str,       # "Bullish" | "Bearish" | "Neutral"
    }
"""


# ---------------------------------------------------------------------------
# Label mapping
# ---------------------------------------------------------------------------

SENTIMENT_TO_SCORE: Dict[str, float] = {
    "Bullish": 1.0,
    "Neutral": 0.0,
    "Bearish": -1.0,
}


def sentiment_label(avg_score: float) -> str:
    """Map an average score to a sentiment label."""
    if avg_score >= 0.2:
        return "Bullish"
    if avg_score <= -0.2:
        return "Bearish"
    return "Neutral"


# ---------------------------------------------------------------------------
# Group articles by date
# ---------------------------------------------------------------------------

def group_by_date(
    records: List[SentimentRecord],
    fallback_date: Optional[str] = None,
) -> Dict[str, List[SentimentRecord]]:
    """
    Group sentiment records by their ``date`` field.

    Records without a ``date`` key are assigned to *fallback_date*
    (defaults to today UTC).

    Args:
        records:       List of SentimentRecord dicts.
        fallback_date: ISO date string (YYYY-MM-DD) for undated records.

    Returns:
        Dict mapping date string → list of records.
    """
    today = fallback_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    grouped: Dict[str, List[SentimentRecord]] = {}

    for r in records:
        raw = r.get("date") or r.get("publishedAt") or ""
        if raw:
            try:
                date_key = raw[:10]  # Take YYYY-MM-DD prefix
            except Exception:
                date_key = today
        else:
            date_key = today

        grouped.setdefault(date_key, []).append(r)

    return grouped


# ---------------------------------------------------------------------------
# Build trend points
# ---------------------------------------------------------------------------

def build_sentiment_trend(
    records: List[SentimentRecord],
    fallback_date: Optional[str] = None,
) -> List[TrendPoint]:
    """
    Aggregate sentiment records into a list of daily TrendPoints.

    Args:
        records:       List of SentimentRecord dicts.
        fallback_date: Fallback date for undated records.

    Returns:
        List of TrendPoint dicts sorted by date ascending.
    """
    if not records:
        return []

    grouped = group_by_date(records, fallback_date)
    trend: List[TrendPoint] = []

    for date_str, day_records in grouped.items():
        scores = []
        bullish = bearish = neutral = 0

        for r in day_records:
            raw_score  = r.get("score")
            raw_label  = r.get("sentiment", "Neutral")

            # Convert label-only records to a numeric score
            if raw_score is not None:
                try:
                    score = float(raw_score)
                except (ValueError, TypeError):
                    score = SENTIMENT_TO_SCORE.get(raw_label, 0.0)
            else:
                score = SENTIMENT_TO_SCORE.get(raw_label, 0.0)

            scores.append(score)

            if raw_label == "Bullish" or score > 0.2:
                bullish += 1
            elif raw_label == "Bearish" or score < -0.2:
                bearish += 1
            else:
                neutral += 1

        avg = round(sum(scores) / len(scores), 4) if scores else 0.0
        trend.append({
            "date":          date_str,
            "avg_score":     avg,
            "bullish_count": bullish,
            "bearish_count": bearish,
            "neutral_count": neutral,
            "total":         len(day_records),
            "label":         sentiment_label(avg),
        })

    # Sort chronologically
    trend.sort(key=lambda x: x["date"])
    return trend


# ---------------------------------------------------------------------------
# Simulate multi-day trend from a single snapshot
# ---------------------------------------------------------------------------

def simulate_trend_from_snapshot(
    records: List[SentimentRecord],
    days: int = 7,
    jitter_seed: int = 42,
) -> List[TrendPoint]:
    """
    When only a single day's articles are available, synthesise a plausible
    *N*-day trend by applying small deterministic jitter to the base score.

    This is used for demonstration / onboarding when no historical data exists.

    Args:
        records:     Today's sentiment records.
        days:        Number of trend days to synthesise.
        jitter_seed: Seed for reproducible jitter sequence.

    Returns:
        List of TrendPoint dicts, oldest first, ending on today.
    """
    if not records:
        return []

    # Compute today's average
    scores = []
    for r in records:
        raw = r.get("score")
        lbl = r.get("sentiment", "Neutral")
        if raw is not None:
            try:
                scores.append(float(raw))
            except (ValueError, TypeError):
                scores.append(SENTIMENT_TO_SCORE.get(lbl, 0.0))
        else:
            scores.append(SENTIMENT_TO_SCORE.get(lbl, 0.0))

    base_avg = sum(scores) / len(scores) if scores else 0.0

    # Simple LCG for deterministic pseudo-random jitter (no external deps)
    def lcg(seed: int) -> float:
        seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
        return seed / 0xFFFFFFFF, seed

    today = datetime.now(timezone.utc).date()
    trend: List[TrendPoint] = []
    seed = jitter_seed

    for i in range(days):
        day = today - timedelta(days=(days - 1 - i))
        jit, seed = lcg(seed)
        jitter = (jit - 0.5) * 0.4  # ±0.2 range
        avg = round(max(-1.0, min(1.0, base_avg + jitter)), 4)

        b = round(len(records) * max(0, (avg + 1) / 2))
        be = round(len(records) * max(0, (-avg + 1) / 2))
        n = len(records) - b - be

        trend.append({
            "date":          day.strftime("%Y-%m-%d"),
            "avg_score":     avg,
            "bullish_count": b,
            "bearish_count": be,
            "neutral_count": max(0, n),
            "total":         len(records),
            "label":         sentiment_label(avg),
        })

    return trend


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------

def trend_direction(trend: List[TrendPoint]) -> str:
    """
    Determine the overall trend direction from a list of TrendPoints.

    Returns:
        'Improving', 'Deteriorating', or 'Stable'.
    """
    if len(trend) < 2:
        return "Stable"
    first_half = trend[: len(trend) // 2]
    second_half = trend[len(trend) // 2 :]
    avg_first  = sum(p["avg_score"] for p in first_half)  / len(first_half)
    avg_second = sum(p["avg_score"] for p in second_half) / len(second_half)
    delta = avg_second - avg_first
    if delta > 0.1:
        return "Improving"
    if delta < -0.1:
        return "Deteriorating"
    return "Stable"


def trend_summary_text(ticker: str, trend: List[TrendPoint]) -> str:
    """Generate a one-paragraph sentiment trend summary."""
    if not trend:
        return "_No trend data available._"

    direction = trend_direction(trend)
    latest    = trend[-1]
    earliest  = trend[0]
    n_days    = len(trend)

    arrow = {"Improving": "📈", "Deteriorating": "📉", "Stable": "➡️"}.get(direction, "")

    return (
        f"Over the past **{n_days} day(s)**, **{ticker}** sentiment trended "
        f"**{direction}** {arrow}. "
        f"The earliest reading ({earliest['date']}) averaged a score of "
        f"**{earliest['avg_score']:+.2f}** ({earliest['label']}), "
        f"while the most recent ({latest['date']}) shows "
        f"**{latest['avg_score']:+.2f}** ({latest['label']}). "
        f"Bullish articles today: **{latest['bullish_count']}**, "
        f"Bearish: **{latest['bearish_count']}**."
    )
