"""
Sector Heatmap Tool for MarketPulse.

Aggregates real-time market data across tickers to produce a sector-level
performance heatmap: average return, volatility score, momentum label,
and a composite heat score (0–100) that indicates sector strength.

No LLM call required — purely quantitative.
"""

from typing import Any, Dict, List, Optional
import statistics


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

TickerSnapshot = Dict[str, Any]
"""
A single ticker's market snapshot:
    {
        "ticker":      str,
        "sector":      str,
        "change_pct":  float,   # 1-day % price change
        "rsi":         float,   # optional RSI value
        "volume":      int,     # optional trading volume
    }
"""

SectorStats = Dict[str, Any]
"""
Aggregated stats for one sector:
    {
        "sector":          str,
        "ticker_count":    int,
        "avg_change_pct":  float,
        "max_change_pct":  float,
        "min_change_pct":  float,
        "avg_rsi":         float | None,
        "gainers":         int,
        "losers":          int,
        "heat_score":      float,   # 0–100
        "momentum":        str,     # "Strong Buy" / "Bullish" / "Neutral" / "Bearish" / "Strong Sell"
        "tickers":         list[str],
    }
"""


# ---------------------------------------------------------------------------
# Momentum classification
# ---------------------------------------------------------------------------

def classify_momentum(heat_score: float) -> str:
    """Classify a sector heat score into a human-readable momentum label."""
    if heat_score >= 80:
        return "Strong Buy"
    if heat_score >= 60:
        return "Bullish"
    if heat_score >= 40:
        return "Neutral"
    if heat_score >= 20:
        return "Bearish"
    return "Strong Sell"


# ---------------------------------------------------------------------------
# Heat score computation
# ---------------------------------------------------------------------------

def compute_heat_score(
    avg_change_pct: float,
    avg_rsi: Optional[float],
    gainer_ratio: float,
) -> float:
    """
    Compute a composite sector heat score between 0 and 100.

    Weights:
        - avg_change_pct  → 50 % (normalised to ±10 % range)
        - avg_rsi         → 30 % (normalised 0–100 RSI scale)
        - gainer_ratio    → 20 % (fraction of tickers that are positive)

    Args:
        avg_change_pct: Average 1-day price change across sector tickers.
        avg_rsi:        Average RSI (None if unavailable; substituted with 50).
        gainer_ratio:   Fraction of tickers with positive change (0.0–1.0).

    Returns:
        Float heat score clamped to [0, 100].
    """
    # Component 1 — price change (clip to ±10 %, map to 0–100)
    clipped = max(-10.0, min(10.0, avg_change_pct))
    change_score = (clipped + 10.0) / 20.0 * 100.0

    # Component 2 — RSI (0–100 already; neutral at 50)
    rsi_score = avg_rsi if avg_rsi is not None else 50.0

    # Component 3 — gainer ratio (0–100)
    gainer_score = gainer_ratio * 100.0

    composite = (
        change_score * 0.50
        + rsi_score * 0.30
        + gainer_score * 0.20
    )
    return round(max(0.0, min(100.0, composite)), 1)


# ---------------------------------------------------------------------------
# Per-sector aggregation
# ---------------------------------------------------------------------------

def aggregate_sector(
    sector: str,
    snapshots: List[TickerSnapshot],
) -> SectorStats:
    """
    Compute aggregated stats for a single sector from its ticker snapshots.

    Args:
        sector:    Sector name (e.g. "Technology").
        snapshots: List of TickerSnapshot dicts belonging to this sector.

    Returns:
        SectorStats dict.
    """
    changes = [s["change_pct"] for s in snapshots if s.get("change_pct") is not None]
    rsis = [s["rsi"] for s in snapshots if s.get("rsi") is not None]

    if not changes:
        return {
            "sector": sector,
            "ticker_count": len(snapshots),
            "avg_change_pct": 0.0,
            "max_change_pct": 0.0,
            "min_change_pct": 0.0,
            "avg_rsi": None,
            "gainers": 0,
            "losers": 0,
            "heat_score": 50.0,
            "momentum": "Neutral",
            "tickers": [s["ticker"] for s in snapshots],
        }

    avg_change = round(statistics.mean(changes), 2)
    max_change = round(max(changes), 2)
    min_change = round(min(changes), 2)
    avg_rsi = round(statistics.mean(rsis), 1) if rsis else None

    gainers = sum(1 for c in changes if c > 0)
    losers = sum(1 for c in changes if c < 0)
    gainer_ratio = gainers / len(changes) if changes else 0.5

    heat = compute_heat_score(avg_change, avg_rsi, gainer_ratio)
    momentum = classify_momentum(heat)

    return {
        "sector": sector,
        "ticker_count": len(snapshots),
        "avg_change_pct": avg_change,
        "max_change_pct": max_change,
        "min_change_pct": min_change,
        "avg_rsi": avg_rsi,
        "gainers": gainers,
        "losers": losers,
        "heat_score": heat,
        "momentum": momentum,
        "tickers": [s["ticker"] for s in snapshots],
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def build_sector_heatmap(
    snapshots: List[TickerSnapshot],
) -> List[SectorStats]:
    """
    Build a full sector heatmap from a list of ticker snapshots.

    Groups tickers by sector, computes per-sector stats, and returns
    the sectors sorted by heat score descending (hottest first).

    Args:
        snapshots: List of TickerSnapshot dicts — each must contain
                   at minimum ``ticker`` and ``sector`` keys.

    Returns:
        List of SectorStats dicts, hottest sector first.
    """
    if not snapshots:
        return []

    # Group by sector
    sector_map: Dict[str, List[TickerSnapshot]] = {}
    for snap in snapshots:
        sector = snap.get("sector") or "Unknown"
        sector_map.setdefault(sector, []).append(snap)

    # Aggregate each sector
    results = [
        aggregate_sector(sector, tickers)
        for sector, tickers in sector_map.items()
    ]

    # Sort hottest → coolest
    results.sort(key=lambda s: s["heat_score"], reverse=True)
    return results


def get_top_and_bottom_sectors(
    heatmap: List[SectorStats],
    n: int = 3,
) -> Dict[str, List[SectorStats]]:
    """
    Return the top-n and bottom-n sectors from a computed heatmap.

    Args:
        heatmap: Output of ``build_sector_heatmap()`` (sorted hottest first).
        n:       Number of sectors to return in each group.

    Returns:
        Dict with keys ``top`` and ``bottom``.
    """
    return {
        "top": heatmap[:n],
        "bottom": heatmap[-n:] if len(heatmap) >= n else heatmap,
    }
