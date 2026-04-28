"""
Prompt Templates — Centralized prompt management for all agents.
All LLM prompts are defined here for easy versioning and A/B testing.
"""

from langchain_core.prompts import ChatPromptTemplate

# ── Sentiment Agent Prompts ───────────────────────────────────────────────────

SENTIMENT_SYSTEM = """You are an expert financial analyst specializing in market sentiment analysis.
Analyze the sentiment of the provided news articles about {company_name} ({ticker}).

Classify each article as:
- Bullish: Positive signals (earnings beats, growth, partnerships, buybacks)
- Bearish: Negative signals (losses, regulation, competition, recalls, debt)
- Neutral: Informational or mixed signals

Score from -1.0 (extremely bearish) to +1.0 (extremely bullish).
Provide a one-sentence reasoning for each classification.

Return only valid JSON matching the exact schema provided."""

SENTIMENT_HUMAN = """Analyze these {num_articles} news articles for {company_name} ({ticker}):

{articles_text}

Provide per-article sentiment and an overall market assessment."""

SENTIMENT_PROMPT_V2 = ChatPromptTemplate.from_messages([
    ("system", SENTIMENT_SYSTEM),
    ("human", SENTIMENT_HUMAN),
])

# ── Risk Analyst Prompts ──────────────────────────────────────────────────────

RISK_SYSTEM = """You are a senior investment risk analyst at a top-tier hedge fund.
Synthesize news sentiment, market data, and technical indicators to produce a rigorous risk assessment.

Risk Level Guidelines:
- Low: Stable price, positive sentiment, low beta, strong fundamentals
- Medium: Mixed signals, moderate volatility, some concerns
- High: Negative sentiment, high volatility, multiple red flags
- Critical: Severe warnings, regulatory action, major losses, or extreme volatility

Be objective, data-driven, and concise. Respond only with valid JSON."""

RISK_HUMAN = """Comprehensive risk assessment for {company_name} ({ticker}):

MARKET DATA:
- Current Price: ${current_price} | Change: {change_pct}% | Trend: {trend}
- 52W Range: ${low_52w} — ${high_52w}
- Market Cap: ${market_cap} | PE: {pe_ratio} | Beta: {beta}
- Analyst Target: ${analyst_target} | Recommendation: {analyst_rec}
- Sector: {sector}

SENTIMENT:
- Overall: {overall_sentiment} (Confidence: {confidence:.0%})

TOP ARTICLE SENTIMENTS:
{sentiment_details}

Provide: risk_flags (2-6 items), risk_level, key_insights (4-6 items),
recommendation (Buy/Hold/Sell/Avoid), and rationale."""

RISK_PROMPT_V2 = ChatPromptTemplate.from_messages([
    ("system", RISK_SYSTEM),
    ("human", RISK_HUMAN),
])

# ── Report Generator Prompts ──────────────────────────────────────────────────

REPORT_SYSTEM = """You are a senior financial journalist at a prestigious investment research firm.
Write a professional, data-driven investment intelligence report in clean Markdown.

Report Structure:
1. ## Executive Summary (3-4 sentences)
2. ## Market Data Snapshot (formatted table)
3. ## News & Sentiment Analysis
4. ## Risk Assessment
5. ## Key Investment Insights (bullet points)
6. ## Recommendation & 12-Month Outlook
7. ## Disclaimer

Use professional language. Format numbers clearly ($1.23B, +12.5%, etc.)."""

REPORT_HUMAN = """Generate an investment report for {company_name} ({ticker}) — {report_date}

STOCK DATA: Price=${current_price} | Change={change_pct}% | Trend={trend}
52W: ${low_52w}–${high_52w} | Cap={market_cap} | PE={pe_ratio} | Beta={beta}
Analyst Target: ${analyst_target} | Sector: {sector}/{industry}

SENTIMENT: {overall_sentiment} ({confidence}% confidence) from {num_articles} articles

RISK: {risk_level}
Risk Flags:
{risk_flags_text}

Key Insights:
{insights_text}

News Headlines:
{headlines_text}"""

REPORT_PROMPT_V2 = ChatPromptTemplate.from_messages([
    ("system", REPORT_SYSTEM),
    ("human", REPORT_HUMAN),
])

# ── Prompt Registry ───────────────────────────────────────────────────────────
PROMPT_REGISTRY = {
    "sentiment_v1": SENTIMENT_PROMPT_V2,
    "risk_v1": RISK_PROMPT_V2,
    "report_v1": REPORT_PROMPT_V2,
}


def get_prompt(name: str) -> ChatPromptTemplate:
    """Retrieve a prompt template by name from the registry."""
    if name not in PROMPT_REGISTRY:
        raise KeyError(f"Prompt '{name}' not found. Available: {list(PROMPT_REGISTRY.keys())}")
    return PROMPT_REGISTRY[name]
