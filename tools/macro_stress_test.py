"""
MarketPulse — Macroeconomic Inflation & Rate Stress Testing Engine
Simulates portfolio valuation shock impacts under interest rate hikes, stagflation, and recession scenarios.
"""

from typing import Any, Dict


def run_macro_stress_test(total_value: float, beta: float = 1.0) -> Dict[str, Any]:
    """
    Simulates portfolio shocks across 3 macroeconomic stress scenarios.

    Args:
        total_value: Total portfolio dollar value
        beta: Portfolio beta market sensitivity

    Returns:
        Dict with shock impacts for Rate Hike, Stagflation, and Deep Recession.
    """
    if not total_value or total_value <= 0:
        return {"error": "Invalid portfolio value for stress testing."}

    b = max(0.2, beta)

    # Scenarios: (Name, Benchmark Shock %)
    scenarios = [
        ("Interest Rate Hike (+200bps)", -0.08 * b),
        ("Stagflation Shock", -0.15 * b),
        ("Global Recession", -0.25 * b),
    ]

    results = []
    for name, drop_pct in scenarios:
        impact_dollars = round(total_value * drop_pct, 2)
        projected_val = round(total_value + impact_dollars, 2)
        results.append({
            "scenario": name,
            "simulated_drop_pct": round(drop_pct * 100.0, 2),
            "estimated_pnl_loss": impact_dollars,
            "projected_portfolio_value": projected_val,
        })

    return {
        "starting_value": total_value,
        "portfolio_beta": b,
        "scenarios": results,
    }
