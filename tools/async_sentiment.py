"""
MarketPulse — Asynchronous Multi-Ticker News Sentiment Batch Processor
Concurrently computes news article sentiment using thread pool execution.
"""

from typing import Any, Dict, List
from tools.async_executor import run_batch_parallel


def batch_score_news_sentiment(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scores list of news articles concurrently.
    """
    if not articles:
        return []

    def _score_one(art: Dict[str, Any]) -> Dict[str, Any]:
        title = art.get("title", "")
        # Heuristic scoring
        if any(w in title.lower() for w in ["soar", "gain", "profit", "surge", "beat"]):
            score = 0.8
            sentiment = "Bullish"
        elif any(w in title.lower() for w in ["drop", "fall", "loss", "plunge", "miss"]):
            score = -0.8
            sentiment = "Bearish"
        else:
            score = 0.0
            sentiment = "Neutral"

        return {**art, "sentiment_score": score, "sentiment": sentiment}

    scored = run_batch_parallel(_score_one, articles, max_workers=5)
    return list(scored.values())
