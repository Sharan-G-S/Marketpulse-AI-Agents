"""
News Fetcher Agent
Responsible for scraping and collecting financial news articles
for a given ticker/company using LangChain tools + LLM.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Any

from graph.state import MarketPulseState
from tools.news_tools import fetch_financial_news, fetch_top_headlines


def get_llm():
    """Lazy-load the configured LLM."""
    from config.settings import LLM_PROVIDER, LLM_MODEL, OPENAI_API_KEY, GOOGLE_API_KEY

    if LLM_PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=GOOGLE_API_KEY)
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY, temperature=0)


def news_agent(state: MarketPulseState) -> MarketPulseState:
    """
    News Fetcher Agent Node.

    Fetches recent financial news for the target company and stores
    cleaned article data into the shared state.
    """
    ticker = state["ticker"]
    company_name = state["company_name"]

    print(f"\n[📰 News Agent] Fetching news for {company_name} ({ticker})...")

    # Use tool to fetch news
    query = f"{company_name} {ticker}"
    articles = fetch_financial_news.invoke({"query": query, "days_back": 7})

    # Filter out errored articles
    valid_articles = [a for a in articles if "error" not in a]

    if not valid_articles:
        print("[📰 News Agent] No news found, using headlines fallback.")
        valid_articles = fetch_top_headlines.invoke({"category": "business"})

    print(f"[📰 News Agent] ✅ Fetched {len(valid_articles)} articles.")

    return {
        **state,
        "raw_news": valid_articles,
        "news_fetched": True,
        "messages": [f"[News Agent] Fetched {len(valid_articles)} articles for {company_name}."],
    }
