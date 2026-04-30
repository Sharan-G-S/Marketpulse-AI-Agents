"""
Sentiment Analyst Agent
Uses an LLM to analyze the sentiment of each news article
and produce an overall market sentiment score.
"""

from typing import Any, Dict, List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from graph.state import MarketPulseState


def get_llm():
    from config.settings import GOOGLE_API_KEY, LLM_MODEL, LLM_PROVIDER, OPENAI_API_KEY
    if LLM_PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=GOOGLE_API_KEY, temperature=0)
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY, temperature=0)


# ── Pydantic schema for structured output ─────────────────────────────────────
class ArticleSentiment(BaseModel):
    title: str = Field(description="Article title")
    sentiment: str = Field(description="Bullish | Bearish | Neutral")
    score: float = Field(description="Sentiment score from -1.0 (very bearish) to +1.0 (very bullish)")
    reasoning: str = Field(description="One sentence explaining the sentiment classification")


class SentimentAnalysis(BaseModel):
    articles: List[ArticleSentiment]
    overall_sentiment: str = Field(description="Bullish | Bearish | Neutral")
    confidence: float = Field(description="Confidence 0.0–1.0")
    summary: str = Field(description="Two-sentence market sentiment summary")


SENTIMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial analyst specializing in sentiment analysis.
Analyze the sentiment of the provided news articles about {company_name} ({ticker}).

For each article, determine:
- sentiment: Bullish (positive for stock price), Bearish (negative), or Neutral
- score: float from -1.0 (very bearish) to +1.0 (very bullish)
- reasoning: concise one-sentence explanation

Then provide:
- overall_sentiment: weighted overall sentiment across all articles
- confidence: how confident you are in the overall assessment (0.0–1.0)
- summary: 2-sentence market sentiment summary

Respond ONLY with valid JSON matching the required schema."""),
    ("human", """News articles to analyze:

{articles_text}

Analyze the sentiment for each article and provide the overall market sentiment for {company_name}."""),
])


def sentiment_agent(state: MarketPulseState) -> MarketPulseState:
    """
    Sentiment Analyst Agent Node.

    Analyzes news articles using an LLM and produces structured
    sentiment scores and overall market sentiment.
    """
    ticker = state["ticker"]
    company_name = state["company_name"]
    raw_news = state.get("raw_news", [])

    print(f"\n[🧠 Sentiment Agent] Analyzing sentiment for {len(raw_news)} articles...")

    if not raw_news:
        return {
            **state,
            "sentiment_scores": [],
            "overall_sentiment": "Neutral",
            "sentiment_confidence": 0.0,
            "sentiment_done": True,
            "messages": ["[Sentiment Agent] No articles to analyze."],
        }

    # Format articles for the prompt
    articles_text = "\n\n".join([
        f"[{i+1}] Title: {a.get('title', 'N/A')}\n"
        f"    Source: {a.get('source', 'Unknown')} | Published: {a.get('publishedAt', 'N/A')}\n"
        f"    Description: {a.get('description', '')}\n"
        f"    Content: {a.get('content', '')[:300]}"
        for i, a in enumerate(raw_news[:8])  # Limit to 8 articles for token efficiency
    ])

    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=SentimentAnalysis)

    try:
        chain = SENTIMENT_PROMPT | llm | parser
        result = chain.invoke({
            "company_name": company_name,
            "ticker": ticker,
            "articles_text": articles_text,
        })

        articles_sentiment = result.get("articles", [])
        overall = result.get("overall_sentiment", "Neutral")
        confidence = result.get("confidence", 0.5)

        print(f"[🧠 Sentiment Agent] ✅ Overall sentiment: {overall} (confidence: {confidence:.0%})")

        return {
            **state,
            "sentiment_scores": articles_sentiment,
            "overall_sentiment": overall,
            "sentiment_confidence": confidence,
            "sentiment_done": True,
            "messages": [
                f"[Sentiment Agent] Analyzed {len(articles_sentiment)} articles. "
                f"Overall: {overall} ({confidence:.0%} confidence)."
            ],
        }

    except Exception as e:
        print(f"[🧠 Sentiment Agent] ⚠️  Error: {e}")
        return {
            **state,
            "sentiment_scores": [],
            "overall_sentiment": "Neutral",
            "sentiment_confidence": 0.0,
            "sentiment_done": True,
            "error": str(e),
            "messages": [f"[Sentiment Agent] Error during analysis: {e}"],
        }
