"""
Unit tests for tools/monte_carlo.py
"""

from tools.monte_carlo import run_monte_carlo_simulation


def test_run_monte_carlo_simulation_valid():
    res = run_monte_carlo_simulation(100.0, days=30, num_simulations=500)
    assert res["starting_price"] == 100.0
    assert "mean_final_price" in res
    assert "var_95_pct" in res
    assert res["simulations_run"] == 500


def test_run_monte_carlo_simulation_invalid():
    res = run_monte_carlo_simulation(0.0)
    assert "error" in res
