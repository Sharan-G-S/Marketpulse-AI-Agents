"""
Report Generator Agent
Synthesizes all agent outputs into a professional, markdown-formatted
investment intelligence report and saves it to disk.
"""

from datetime import datetime, timezone
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.alert_engine import format_alert_summary
from agents.watchlist_agent import format_watchlist_table
from config.settings import REPORT_OUTPUT_DIR
from graph.state import MarketPulseState


def get_llm():
    from config.settings import GOOGLE_API_KEY, LLM_MODEL, LLM_PROVIDER, OPENAI_API_KEY
    if LLM_PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=GOOGLE_API_KEY, temperature=0.3)
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY, temperature=0.3)


REPORT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior financial journalist at a prestigious investment research firm.
Write a professional, data-driven investment intelligence report in clean Markdown format.

The report must include these sections:
1. Executive Summary
2. Market Data Snapshot (formatted table)
3. News & Sentiment Analysis
4. Risk Assessment
5. Market Watchlist Context (if provided)
6. Portfolio Health (if provided)
7. Alerts & Warnings (if any)
8. Key Investment Insights
9. Recommendation & Outlook
10. Disclaimer

Use professional financial language. Be factual, precise, and insightful.
Format numbers properly (e.g., $1.23B, +12.5%, etc.)."""),
    ("human", """Generate a complete investment report for:

**Company:** {company_name} ({ticker})
**Report Date:** {report_date}
**Analysis Depth:** {analysis_depth}

== STOCK MARKET DATA ==
Current Price: ${current_price}
Day Change: {change_pct}%
Trend: {trend}
52-Week High/Low: ${high_52w} / ${low_52w}
Market Cap: ${market_cap}
PE Ratio: {pe_ratio}
Beta: {beta}
Analyst Target Price: ${analyst_target}
Sector: {sector} | Industry: {industry}

== SENTIMENT ==
Overall Sentiment: {overall_sentiment}
Confidence: {confidence}%
News Articles Analyzed: {num_articles}

== RISK ASSESSMENT ==
Risk Level: {risk_level}

Risk Flags:
{risk_flags_text}

== KEY INSIGHTS ==
{insights_text}

== ARTICLE HEADLINES ==
{headlines_text}

== WATCHLIST CONTEXT ==
{watchlist_table}

== PORTFOLIO SUMMARY ==
{portfolio_summary}

== ALERTS ==
{alert_summary}

Write the full investment report now."""),
])


def report_agent(state: MarketPulseState) -> MarketPulseState:
    """
    Report Generator Agent Node.

    Compiles all agent outputs into a comprehensive investment report,
    saves it as a markdown file, and updates the shared state.
    """
    ticker = state["ticker"]
    company_name = state["company_name"]
    stock = state.get("stock_summary", {})
    raw_news = state.get("raw_news", [])
    risk_flags = state.get("risk_flags", [])
    key_insights = state.get("key_insights", [])
    depth = state.get("analysis_depth", "standard")
    watchlist = state.get("watchlist") or stock.get("watchlist", [])
    portfolio_summary = state.get("portfolio_summary", {})
    alerts = state.get("alerts", [])

    print(f"\n[📄 Report Agent] Generating investment report for {ticker}...")

    # Format helper fields
    risk_flags_text = "\n".join(f"• {f}" for f in risk_flags) or "• No significant flags identified"
    insights_text = "\n".join(f"• {i}" for i in key_insights) or "• Insufficient data for insights"
    headlines_text = "\n".join(
        f"• [{a.get('source', 'Unknown')}] {a.get('title', 'N/A')}"
        for a in raw_news[:6]
    ) or "• No articles available"

    watchlist_table = format_watchlist_table(watchlist) if watchlist else "No watchlist data available."
    portfolio_text = _format_portfolio_summary(portfolio_summary)
    alert_summary = format_alert_summary(alerts) or "No alerts generated."

    market_cap = stock.get("market_cap", 0) or 0
    market_cap_str = (
        f"{market_cap / 1e12:.2f}T" if market_cap > 1e12
        else f"{market_cap / 1e9:.2f}B" if market_cap > 1e9
        else f"{market_cap / 1e6:.2f}M" if market_cap > 1e6
        else str(market_cap)
    )

    llm = get_llm()
    chain = REPORT_PROMPT | llm | StrOutputParser()

    try:
        report_md = chain.invoke({
            "company_name": company_name,
            "ticker": ticker,
            "report_date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
            "analysis_depth": depth.capitalize(),
            "current_price": stock.get("current_price", "N/A"),
            "change_pct": stock.get("change_pct", 0),
            "trend": stock.get("trend", "N/A"),
            "high_52w": stock.get("52w_high", "N/A"),
            "low_52w": stock.get("52w_low", "N/A"),
            "market_cap": market_cap_str,
            "pe_ratio": stock.get("pe_ratio", "N/A"),
            "beta": stock.get("beta", "N/A"),
            "analyst_target": stock.get("analyst_target_price", "N/A"),
            "sector": stock.get("sector", "N/A"),
            "industry": stock.get("industry", "N/A"),
            "overall_sentiment": state.get("overall_sentiment", "Neutral"),
            "confidence": int(state.get("sentiment_confidence", 0.0) * 100),
            "num_articles": len(raw_news),
            "risk_level": state.get("risk_level", "Medium"),
            "risk_flags_text": risk_flags_text,
            "insights_text": insights_text,
            "headlines_text": headlines_text,
            "watchlist_table": watchlist_table,
            "portfolio_summary": portfolio_text,
            "alert_summary": alert_summary,
        })

        # Save report to disk
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_{timestamp}_report.md"
        report_path = os.path.join(REPORT_OUTPUT_DIR, filename)

        os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        print(f"[📄 Report Agent] ✅ Report saved: {report_path}")

        return {
            **state,
            "final_report": report_md,
            "report_path": report_path,
            "report_done": True,
            "messages": [f"[Report Agent] Investment report generated and saved to {report_path}."],
        }

    except Exception as e:
        print(f"[📄 Report Agent] ⚠️  Error: {e}")
        # Fallback: generate a simple report
        fallback_report = _generate_fallback_report(state, stock, risk_flags, key_insights)
        return {
            **state,
            "final_report": fallback_report,
            "report_path": None,
            "report_done": True,
            "error": str(e),
            "messages": [f"[Report Agent] Generated fallback report due to error: {e}"],
        }


def _generate_fallback_report(state, stock, risk_flags, key_insights) -> str:
    """Generate a simple markdown report without LLM if there's an error."""
    ticker = state["ticker"]
    company_name = state["company_name"]
    now = datetime.now(timezone.utc).strftime("%B %d, %Y")
    watchlist = state.get("watchlist") or stock.get("watchlist", [])
    portfolio_summary = state.get("portfolio_summary", {})
    alerts = state.get("alerts", [])

    return f"""# MarketPulse Investment Report
## {company_name} ({ticker})
*Generated: {now}*

---

## Executive Summary
This report provides a financial intelligence overview for {company_name} ({ticker}).

## Market Data Snapshot
| Metric | Value |
|--------|-------|
| Current Price | ${stock.get('current_price', 'N/A')} |
| Price Change | {stock.get('change_pct', 0):.2f}% |
| 52-Week High | ${stock.get('52w_high', 'N/A')} |
| 52-Week Low | ${stock.get('52w_low', 'N/A')} |
| PE Ratio | {stock.get('pe_ratio', 'N/A')} |
| Beta | {stock.get('beta', 'N/A')} |

## Sentiment
**Overall:** {state.get('overall_sentiment', 'Neutral')}

## Risk Assessment
**Risk Level:** {state.get('risk_level', 'Medium')}

### Risk Flags
{''.join(f'- {f}' + chr(10) for f in risk_flags) or '- No major risk flags identified'}

## Key Insights
{''.join(f'- {i}' + chr(10) for i in key_insights) or '- Insufficient data'}

## Market Watchlist Context
{format_watchlist_table(watchlist) if watchlist else 'No watchlist data available.'}

## Portfolio Health
{_format_portfolio_summary(portfolio_summary)}

## Alerts & Warnings
{format_alert_summary(alerts) or 'No alerts generated.'}

---
*This report is generated by MarketPulse AI and is for informational purposes only.*
"""


def _format_portfolio_summary(portfolio: dict) -> str:
    """Format portfolio analysis results into a readable markdown block."""
    if not portfolio:
        return "No portfolio data provided."
    if portfolio.get("error"):
        return f"Portfolio analysis error: {portfolio.get('error')}"

    lines = [
        f"Total Value: ${portfolio.get('total_market_value', 0):,.2f}",
        f"Total P&L: ${portfolio.get('total_unrealised_pnl', 0):,.2f} ({portfolio.get('total_pnl_pct', 0):.2f}%)",
        f"Diversification: {portfolio.get('diversification_label', 'N/A')} ({portfolio.get('diversification_score', 0)} / 100)",
    ]
    if portfolio.get("portfolio_beta") is not None:
        lines.append(f"Portfolio Beta: {portfolio.get('portfolio_beta')}")
    if portfolio.get("health_summary"):
        lines.append("\n" + portfolio.get("health_summary"))

    return "\n".join(lines)
