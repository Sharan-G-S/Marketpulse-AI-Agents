"""
Web Search Tool
DuckDuckGo-based fallback search for finding company info,
analyst ratings, and supplemental financial context.
"""

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from typing import List, Dict, Any


_search_run = DuckDuckGoSearchRun()
_search_results = DuckDuckGoSearchResults(num_results=5)


@tool
def web_search(query: str) -> str:
    """
    Perform a web search using DuckDuckGo and return a text summary.
    Use this to find supplemental financial context, analyst opinions,
    or company background information.
    """
    try:
        return _search_run.run(query)
    except Exception as e:
        return f"Search failed: {e}"


@tool
def web_search_results(query: str) -> List[Dict[str, Any]]:
    """
    Perform a web search and return structured results with title, link, and snippet.
    Returns up to 5 results for a given financial query.
    """
    try:
        raw = _search_results.run(query)
        # Parse the raw string into structured results
        results = []
        for item in raw.split("], ["):
            try:
                snippet = item.strip("[]").strip()
                results.append({"snippet": snippet})
            except Exception:
                continue
        return results if results else [{"snippet": raw}]
    except Exception as e:
        return [{"error": str(e), "snippet": ""}]


@tool
def search_analyst_ratings(ticker: str) -> str:
    """
    Search for the latest analyst ratings and price targets for a stock ticker.
    Returns a text summary of analyst consensus and target prices.
    """
    query = f"{ticker} stock analyst rating price target 2024 2025 Wall Street consensus"
    try:
        return _search_run.run(query)
    except Exception as e:
        return f"Could not retrieve analyst ratings: {e}"


@tool
def search_company_background(company_name: str) -> str:
    """
    Search for background information about a company including
    business model, competitive position, and recent developments.
    """
    query = f"{company_name} business model competitive advantages recent news 2025"
    try:
        return _search_run.run(query)
    except Exception as e:
        return f"Could not retrieve company background: {e}"
