"""
MarketPulse — Monte Carlo Simulation Engine
Runs stochastic Geometric Brownian Motion simulations for risk distribution modeling.
"""

from typing import Dict, List
import numpy as np


def run_monte_carlo_simulation(
    current_price: float,
    annual_return: float = 0.10,
    annual_volatility: float = 0.20,
    days: int = 30,
    num_simulations: int = 1000,
) -> Dict:
    """
    Simulates future price distribution using Geometric Brownian Motion (GBM).

    Args:
        current_price: Starting asset price
        annual_return: Expected annual drift return
        annual_volatility: Expected annual volatility
        days: Simulation horizon in trading days
        num_simulations: Number of stochastic paths to sample

    Returns:
        Dict with mean price, 95% VaR percentage, 5th percentile price, and 95th percentile price.
    """
    if not current_price or current_price <= 0:
        return {"error": "Invalid current price for Monte Carlo simulation."}

    dt = 1.0 / 252.0  # Daily time step
    mu = annual_return
    sigma = annual_volatility

    np.random.seed(42)
    # Generate daily returns for num_simulations paths
    daily_returns = np.random.normal(
        (mu - 0.5 * sigma**2) * dt,
        sigma * np.sqrt(dt),
        (days, num_simulations),
    )

    price_paths = np.zeros((days + 1, num_simulations))
    price_paths[0] = current_price

    for t in range(1, days + 1):
        price_paths[t] = price_paths[t - 1] * np.exp(daily_returns[t - 1])

    final_prices = price_paths[-1]

    pct_5 = np.percentile(final_prices, 5)
    pct_50 = np.percentile(final_prices, 50)
    pct_95 = np.percentile(final_prices, 95)

    var_95_pct = (current_price - pct_5) / current_price * 100.0

    return {
        "starting_price": current_price,
        "mean_final_price": round(float(np.mean(final_prices)), 2),
        "median_final_price": round(float(pct_50), 2),
        "percentile_5th": round(float(pct_5), 2),
        "percentile_95th": round(float(pct_95), 2),
        "var_95_pct": round(float(var_95_pct), 2),
        "days": days,
        "simulations_run": num_simulations,
    }
