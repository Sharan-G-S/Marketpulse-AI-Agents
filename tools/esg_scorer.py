"""
MarketPulse — ESG Sustainability & Corporate Governance Scorer
Evaluates Environmental, Social, and Governance ratings for public companies.
"""

from typing import Any, Dict


def evaluate_esg_score(ticker: str) -> Dict[str, Any]:
    """
    Computes corporate ESG sustainability score (0-100) and risk level.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with environmental_score, social_score, governance_score, total_esg, and rating.
    """
    if not ticker or not isinstance(ticker, str):
        return {"error": "Invalid ticker for ESG evaluation."}

    tk = ticker.strip().upper()
    seed = sum(ord(c) for c in tk)

    # Heuristic mock score derived from ticker string
    env = 50 + (seed % 40)
    soc = 45 + ((seed * 2) % 45)
    gov = 55 + ((seed * 3) % 40)

    total_esg = round((env * 0.35 + soc * 0.35 + gov * 0.30), 1)

    if total_esg >= 75:
        rating = "Leader (A+)"
    elif total_esg >= 60:
        rating = "Average (B)"
    else:
        rating = "Laggard (C)"

    return {
        "ticker": tk,
        "environmental_score": env,
        "social_score": soc,
        "governance_score": gov,
        "total_esg_score": total_esg,
        "esg_rating": rating,
    }
