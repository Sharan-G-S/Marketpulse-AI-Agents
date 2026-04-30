"""
Risk Analyst Agent
Cross-references sentiment data with stock market data to identify
risk flags, generate insights, and assign an overall risk level.
"""

from typing import List

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


# ── Output schema ─────────────────────────────────────────────────────────────
class RiskAnalysis(BaseModel):
    risk_flags: List[str] = Field(description="List of specific risk warnings (2-6 items)")
    risk_level: str = Field(description="Low | Medium | High | Critical")
    key_insights: List[str] = Field(description="4-6 key investment insights as bullet points")
    recommendation: str = Field(description="Buy | Hold | Sell | Avoid")
    rationale: str = Field(description="2-3 sentence explanation of the recommendation")


RISK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior investment risk analyst at a top-tier hedge fund.
Your job is to synthesize news sentiment and stock market data to produce a rigorous risk assessment.

Provide:
1. risk_flags: Specific risks detected (volatility, regulatory, financial health, market conditions, etc.)
2. risk_level: Low / Medium / High / Critical
3. key_insights: 4-6 actionable bullet points for investors
4. recommendation: Buy / Hold / Sell / Avoid
5. rationale: Brief explanation backing the recommendation

Be objective, data-driven, and precise. Respond ONLY with valid JSON."""),
    ("human", """Analyze the following data for {company_name} ({ticker}):

== STOCK MARKET DATA ==
Current Price: ${current_price}
Price Change: {change_pct}% over period
Trend: {trend}
52-Week High: ${high_52w} | 52-Week Low: ${low_52w}
PE Ratio: {pe_ratio}
Beta: {beta}
Market Cap: ${market_cap:,.0f}
Analyst Target: ${analyst_target}
Analyst Recommendation: {analyst_rec}
Sector: {sector}

== SENTIMENT ANALYSIS ==
Overall Sentiment: {overall_sentiment}
Confidence: {confidence:.0%}

Top Article Sentiments:
{sentiment_details}

Based on this data, provide a comprehensive risk assessment."""),
])


def risk_analyst_agent(state: MarketPulseState) -> MarketPulseState:
    """
    Risk Analyst Agent Node.

    Cross-references sentiment and stock data to produce risk flags,
    investment insights, risk level, and actionable recommendation.
    """
    ticker = state["ticker"]
    company_name = state["company_name"]
    stock = state.get("stock_summary", {})
    sentiments = state.get("sentiment_scores", [])

    print(f"\n[⚠️  Risk Agent] Running risk analysis for {ticker}...")

    # Format sentiment details
    sentiment_details = "\n".join([
        f"  • {s.get('title', 'N/A')[:80]}: {s.get('sentiment', 'N/A')} (score: {s.get('score', 0):.2f})"
        for s in sentiments[:5]
    ]) or "  • No article-level sentiment data available"

    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=RiskAnalysis)

    try:
        chain = RISK_PROMPT | llm | parser
        result = chain.invoke({
            "company_name": company_name,
            "ticker": ticker,
            "current_price": stock.get("current_price", "N/A"),
            "change_pct": stock.get("change_pct", 0),
            "trend": stock.get("trend", "N/A"),
            "high_52w": stock.get("52w_high", "N/A"),
            "low_52w": stock.get("52w_low", "N/A"),
            "pe_ratio": stock.get("pe_ratio", "N/A"),
            "beta": stock.get("beta", "N/A"),
            "market_cap": stock.get("market_cap", 0) or 0,
            "analyst_target": stock.get("analyst_target_price", "N/A"),
            "analyst_rec": stock.get("recommendation", "N/A"),
            "sector": stock.get("sector", "N/A"),
            "overall_sentiment": state.get("overall_sentiment", "Neutral"),
            "confidence": state.get("sentiment_confidence", 0.0),
            "sentiment_details": sentiment_details,
        })

        risk_flags = result.get("risk_flags", [])
        risk_level = result.get("risk_level", "Medium")
        key_insights = result.get("key_insights", [])

        print(f"[⚠️  Risk Agent] ✅ Risk Level: {risk_level} | Recommendation: {result.get('recommendation')}")

        # Attach recommendation to stock summary for report use
        updated_stock = {**stock, "recommendation": result.get("recommendation", "Hold")}

        return {
            **state,
            "stock_summary": updated_stock,
            "risk_flags": risk_flags,
            "risk_level": risk_level,
            "key_insights": key_insights,
            "risk_done": True,
            "messages": [
                f"[Risk Agent] Risk Level: {risk_level}. "
                f"{len(risk_flags)} flags raised. Recommendation: {result.get('recommendation', 'Hold')}."
            ],
        }

    except Exception as e:
        print(f"[⚠️  Risk Agent] ⚠️  Error: {e}")
        return {
            **state,
            "risk_flags": ["Unable to complete risk analysis due to an error."],
            "risk_level": "Medium",
            "key_insights": [],
            "risk_done": True,
            "error": str(e),
            "messages": [f"[Risk Agent] Error during risk analysis: {e}"],
        }
