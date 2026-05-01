"""
Financial News Tools
Fetches news articles from NewsAPI and formats them for agent consumption.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from langchain_core.tools import tool
import requests

from config.settings import NEWS_MAX_ARTICLES, NEWSAPI_KEY


@tool
def fetch_financial_news(query: str, days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Fetch recent financial news articles for a company or ticker symbol.
    Returns list of articles with title, description, url, source, and publishedAt.
    """
    if not NEWSAPI_KEY:
        # Return mock data if no API key is configured
        return _mock_news(query)

    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{query} stock finance market",
        "from": from_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": NEWS_MAX_ARTICLES,
        "apiKey": NEWSAPI_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "ok":
            return [{"error": data.get("message", "NewsAPI error"), "title": "Failed to fetch news"}]

        articles = []
        for art in data.get("articles", []):
            title = art.get("title", "")
            url = art.get("url", "")
            if not title or not url:
                continue
            articles.append({
                "title": art.get("title", ""),
                "description": art.get("description", ""),
                "url": art.get("url", ""),
                "source": art.get("source", {}).get("name", "Unknown"),
                "publishedAt": art.get("publishedAt", ""),
                "content": (art.get("content") or "")[:500],   # Truncate for token efficiency
            })
        return articles

    except Exception as e:
        return [{"error": str(e), "title": "Failed to fetch news"}]


@tool
def fetch_top_headlines(category: str = "business") -> List[Dict[str, Any]]:
    """
    Fetch top business/financial headlines from NewsAPI.
    category options: business, technology, science
    """
    if not NEWSAPI_KEY:
        return _mock_news("market headlines")

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": category,
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWSAPI_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return [
            {
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "publishedAt": a.get("publishedAt", ""),
            }
            for a in data.get("articles", [])
        ]
    except Exception as e:
        return [{"error": str(e)}]


def _mock_news(query: str) -> List[Dict[str, Any]]:
    """Returns mock news articles when no API key is set (for development)."""
    return [
        {
            "title": f"{query} Reports Strong Quarterly Earnings Beat",
            "description": f"{query} exceeded analyst expectations with robust revenue growth driven by strong consumer demand.",
            "url": "https://example.com/news/1",
            "source": "Financial Times",
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "content": f"{query} announced quarterly earnings that surpassed Wall Street expectations by 15%...",
        },
        {
            "title": f"Analysts Raise Price Target for {query} After Strong Guidance",
            "description": "Multiple investment banks have updated their outlook following the latest earnings call.",
            "url": "https://example.com/news/2",
            "source": "Bloomberg",
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "content": "Goldman Sachs and Morgan Stanley both revised their 12-month price targets upward...",
        },
        {
            "title": f"{query} Faces Regulatory Scrutiny in European Markets",
            "description": "European regulators have launched a probe into competitive practices.",
            "url": "https://example.com/news/3",
            "source": "Reuters",
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "content": "The investigation could result in substantial fines if antitrust violations are confirmed...",
        },
        {
            "title": f"Institutional Investors Increase Stakes in {query}",
            "description": "Several major hedge funds have disclosed increased positions in their latest 13F filings.",
            "url": "https://example.com/news/4",
            "source": "MarketWatch",
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "content": "Blackrock and Vanguard both increased their holdings significantly this quarter...",
        },
        {
            "title": f"Supply Chain Improvements Boost {query} Margins",
            "description": "Operational efficiencies have led to improved gross margins for the company.",
            "url": "https://example.com/news/5",
            "source": "CNBC",
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "content": "Management highlighted supply chain optimizations as a key driver of margin expansion...",
        },
    ]
