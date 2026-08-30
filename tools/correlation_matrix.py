"""
MarketPulse — Multi-Asset Correlation Heatmap & Risk Clustering Tool
Computes Pearson return correlation matrix across portfolio asset tickers.
"""

from typing import Any, Dict, List
import pandas as pd
import numpy as np


def compute_asset_correlation_matrix(price_histories: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Computes correlation matrix DataFrame from dict of ticker price history lists.
    """
    if not price_histories:
        return {"matrix": {}, "avg_correlation": 0.0}

    closes_df = pd.DataFrame()
    for ticker, hist in price_histories.items():
        if hist and "error" not in hist[0]:
            closes = [r["close"] for r in hist if isinstance(r, dict) and "close" in r]
            if closes:
                closes_df[ticker] = pd.Series(closes)

    if closes_df.empty or closes_df.shape[1] < 2:
        return {"matrix": {}, "avg_correlation": 1.0}

    returns_df = closes_df.pct_change().dropna()
    corr_matrix = returns_df.corr().round(3)

    # Average off-diagonal correlation
    mask = ~np.eye(corr_matrix.shape[0], dtype=bool)
    off_diag = corr_matrix.values[mask]
    avg_corr = round(float(np.mean(off_diag)), 3) if len(off_diag) > 0 else 1.0

    return {
        "matrix": corr_matrix.to_dict(),
        "tickers": list(closes_df.columns),
        "avg_correlation": avg_corr,
        "diversification_rating": "High" if avg_corr < 0.4 else ("Moderate" if avg_corr < 0.7 else "Low"),
    }
