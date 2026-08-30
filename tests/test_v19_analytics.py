"""
Unit tests for v19 analytics tools (fx_arbitrage, correlation_matrix, altman_zscore).
"""

from tools.altman_zscore import calculate_altman_zscore
from tools.correlation_matrix import compute_asset_correlation_matrix
from tools.fx_arbitrage import scan_fx_arbitrage_triangles


def test_scan_fx_arbitrage_triangles():
    res = scan_fx_arbitrage_triangles()
    assert "implied_eur_gbp_cross" in res
    assert res["base_currency"] == "USD"


def test_compute_asset_correlation_matrix():
    data = {
        "AAPL": [{"close": 100.0}, {"close": 102.0}, {"close": 104.0}],
        "MSFT": [{"close": 200.0}, {"close": 204.0}, {"close": 208.0}],
    }
    res = compute_asset_correlation_matrix(data)
    assert "matrix" in res
    assert res["avg_correlation"] > 0.9


def test_calculate_altman_zscore():
    res = calculate_altman_zscore(
        working_capital=50.0,
        retained_earnings=100.0,
        ebit=30.0,
        market_cap=500.0,
        total_revenue=400.0,
        total_assets=300.0,
        total_liabilities=150.0,
    )
    assert res["z_score"] > 0
    assert "zone" in res
