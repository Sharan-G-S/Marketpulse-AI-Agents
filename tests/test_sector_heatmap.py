"""
Tests for tools/sector_heatmap.py
"""

import pytest

from tools.sector_heatmap import (
    aggregate_sector,
    build_sector_heatmap,
    classify_momentum,
    compute_heat_score,
    get_top_and_bottom_sectors,
)


# ---------------------------------------------------------------------------
# classify_momentum
# ---------------------------------------------------------------------------

class TestClassifyMomentum:
    def test_strong_buy(self):
        assert classify_momentum(85.0) == "Strong Buy"

    def test_bullish(self):
        assert classify_momentum(65.0) == "Bullish"

    def test_neutral(self):
        assert classify_momentum(50.0) == "Neutral"

    def test_bearish(self):
        assert classify_momentum(30.0) == "Bearish"

    def test_strong_sell(self):
        assert classify_momentum(10.0) == "Strong Sell"

    def test_boundary_80(self):
        assert classify_momentum(80.0) == "Strong Buy"

    def test_boundary_60(self):
        assert classify_momentum(60.0) == "Bullish"

    def test_boundary_40(self):
        assert classify_momentum(40.0) == "Neutral"

    def test_boundary_20(self):
        assert classify_momentum(20.0) == "Bearish"


# ---------------------------------------------------------------------------
# compute_heat_score
# ---------------------------------------------------------------------------

class TestComputeHeatScore:
    def test_score_clamped_to_100(self):
        score = compute_heat_score(10.0, 100.0, 1.0)
        assert score <= 100.0

    def test_score_clamped_to_0(self):
        score = compute_heat_score(-10.0, 0.0, 0.0)
        assert score >= 0.0

    def test_neutral_inputs(self):
        # avg_change=0, avg_rsi=50, gainer_ratio=0.5 → should be near 50
        score = compute_heat_score(0.0, 50.0, 0.5)
        assert 45.0 <= score <= 55.0

    def test_no_rsi_uses_50_default(self):
        score_with_rsi = compute_heat_score(0.0, 50.0, 0.5)
        score_no_rsi = compute_heat_score(0.0, None, 0.5)
        assert score_with_rsi == score_no_rsi

    def test_extreme_positive(self):
        score = compute_heat_score(10.0, 80.0, 1.0)
        assert score >= 80.0

    def test_extreme_negative(self):
        score = compute_heat_score(-10.0, 20.0, 0.0)
        assert score <= 30.0


# ---------------------------------------------------------------------------
# aggregate_sector
# ---------------------------------------------------------------------------

TECH_SNAPSHOTS = [
    {"ticker": "AAPL", "sector": "Technology", "change_pct": 2.5, "rsi": 62.0},
    {"ticker": "MSFT", "sector": "Technology", "change_pct": 1.8, "rsi": 58.0},
    {"ticker": "NVDA", "sector": "Technology", "change_pct": -0.5, "rsi": 70.0},
]


class TestAggregateSector:
    def test_returns_correct_sector_name(self):
        result = aggregate_sector("Technology", TECH_SNAPSHOTS)
        assert result["sector"] == "Technology"

    def test_ticker_count(self):
        result = aggregate_sector("Technology", TECH_SNAPSHOTS)
        assert result["ticker_count"] == 3

    def test_avg_change_pct(self):
        result = aggregate_sector("Technology", TECH_SNAPSHOTS)
        expected = round((2.5 + 1.8 + -0.5) / 3, 2)
        assert result["avg_change_pct"] == expected

    def test_gainers_and_losers(self):
        result = aggregate_sector("Technology", TECH_SNAPSHOTS)
        assert result["gainers"] == 2
        assert result["losers"] == 1

    def test_heat_score_in_range(self):
        result = aggregate_sector("Technology", TECH_SNAPSHOTS)
        assert 0.0 <= result["heat_score"] <= 100.0

    def test_tickers_list(self):
        result = aggregate_sector("Technology", TECH_SNAPSHOTS)
        assert set(result["tickers"]) == {"AAPL", "MSFT", "NVDA"}

    def test_empty_snapshots(self):
        result = aggregate_sector("Technology", [])
        assert result["heat_score"] == 50.0
        assert result["momentum"] == "Neutral"

    def test_no_rsi_data(self):
        snaps = [{"ticker": "X", "sector": "Energy", "change_pct": 1.0}]
        result = aggregate_sector("Energy", snaps)
        assert result["avg_rsi"] is None


# ---------------------------------------------------------------------------
# build_sector_heatmap
# ---------------------------------------------------------------------------

MULTI_SNAPSHOTS = [
    {"ticker": "AAPL", "sector": "Technology", "change_pct": 2.0, "rsi": 60.0},
    {"ticker": "MSFT", "sector": "Technology", "change_pct": 1.5, "rsi": 55.0},
    {"ticker": "JNJ",  "sector": "Healthcare",  "change_pct": -1.0, "rsi": 42.0},
    {"ticker": "PFE",  "sector": "Healthcare",  "change_pct": -0.5, "rsi": 38.0},
    {"ticker": "XOM",  "sector": "Energy",      "change_pct": 3.0,  "rsi": 68.0},
]


class TestBuildSectorHeatmap:
    def test_returns_list(self):
        result = build_sector_heatmap(MULTI_SNAPSHOTS)
        assert isinstance(result, list)

    def test_sector_count(self):
        result = build_sector_heatmap(MULTI_SNAPSHOTS)
        sectors = {s["sector"] for s in result}
        assert sectors == {"Technology", "Healthcare", "Energy"}

    def test_sorted_hottest_first(self):
        result = build_sector_heatmap(MULTI_SNAPSHOTS)
        scores = [s["heat_score"] for s in result]
        assert scores == sorted(scores, reverse=True)

    def test_empty_input(self):
        result = build_sector_heatmap([])
        assert result == []

    def test_unknown_sector_fallback(self):
        snaps = [{"ticker": "ZZZ", "change_pct": 0.0}]
        result = build_sector_heatmap(snaps)
        assert result[0]["sector"] == "Unknown"


# ---------------------------------------------------------------------------
# get_top_and_bottom_sectors
# ---------------------------------------------------------------------------

class TestGetTopAndBottomSectors:
    def test_top_sectors(self):
        heatmap = build_sector_heatmap(MULTI_SNAPSHOTS)
        tb = get_top_and_bottom_sectors(heatmap, n=1)
        assert len(tb["top"]) == 1

    def test_bottom_sectors(self):
        heatmap = build_sector_heatmap(MULTI_SNAPSHOTS)
        tb = get_top_and_bottom_sectors(heatmap, n=1)
        assert len(tb["bottom"]) == 1

    def test_top_has_highest_score(self):
        heatmap = build_sector_heatmap(MULTI_SNAPSHOTS)
        tb = get_top_and_bottom_sectors(heatmap, n=1)
        assert tb["top"][0]["heat_score"] == max(s["heat_score"] for s in heatmap)
