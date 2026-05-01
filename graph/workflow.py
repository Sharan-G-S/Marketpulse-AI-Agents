"""
LangGraph Workflow — MarketPulse Orchestration

Defines the multi-agent graph: nodes, edges, conditional routing,
and the compiled StateGraph that drives the full analysis pipeline.
"""

from langgraph.graph import END, StateGraph

from agents.alert_engine import alert_agent
from agents.news_agent import news_agent
from agents.portfolio_tracker import portfolio_agent
from agents.report_agent import report_agent
from agents.risk_analyst_agent import risk_analyst_agent
from agents.sentiment_agent import sentiment_agent
from agents.stock_data_agent import stock_data_agent
from agents.watchlist_agent import watchlist_agent
from config.logger import write_json_log
from config.settings import LOG_OUTPUT_DIR, NASDAQ_TICKER_LIST_PATH
from config.utils import load_ticker_list, normalize_ticker, validate_ticker, validate_ticker_against_list
from graph.state import MarketPulseState


# ── Guard: Abort if any critical error is present ─────────────────────────────
def should_continue(state: MarketPulseState) -> str:
    """
    After news + stock data are fetched in parallel,
    check if we have enough data to proceed with analysis.
    """
    if state.get("error") and not state.get("raw_news") and not state.get("stock_fetched"):
        return "report"   # Skip to report with whatever data we have
    return "sentiment"


def after_sentiment(state: MarketPulseState) -> str:
    """Route after sentiment analysis."""
    return "risk"


def after_risk(state: MarketPulseState) -> str:
    """Route after risk analysis."""
    if state.get("portfolio_positions"):
        return "portfolio"
    return "alerts"


def after_portfolio(state: MarketPulseState) -> str:
    """Route after portfolio analysis."""
    return "alerts"


def build_graph() -> StateGraph:
    """
    Build and compile the MarketPulse LangGraph workflow.

    Graph topology:
        [news_agent]  ──┐
                        ├──> [sentiment_agent] ──> [risk_analyst_agent] ──> [report_agent] ──> END
        [stock_agent] ──┘
    """
    workflow = StateGraph(MarketPulseState)

    # ── Register agent nodes ──────────────────────────────────────────────────
    workflow.add_node("news", news_agent)
    workflow.add_node("stock", stock_data_agent)
    workflow.add_node("watchlist", watchlist_agent)
    workflow.add_node("sentiment", sentiment_agent)
    workflow.add_node("risk", risk_analyst_agent)
    workflow.add_node("portfolio", portfolio_agent)
    workflow.add_node("alerts", alert_agent)
    workflow.add_node("report", report_agent)

    # ── Entry point: fetch news and stock data ────────────────────────────────
    workflow.set_entry_point("news")

    # ── Sequential flow ───────────────────────────────────────────────────────
    # news -> stock -> watchlist -> sentiment -> risk -> portfolio? -> alerts -> report -> END
    workflow.add_edge("news", "stock")
    workflow.add_conditional_edges(
        "stock",
        should_continue,
        {"sentiment": "watchlist", "report": "report"},
    )
    workflow.add_edge("watchlist", "sentiment")
    workflow.add_edge("sentiment", "risk")
    workflow.add_conditional_edges(
        "risk",
        after_risk,
        {"portfolio": "portfolio", "alerts": "alerts"},
    )
    workflow.add_conditional_edges(
        "portfolio",
        after_portfolio,
        {"alerts": "alerts"},
    )
    workflow.add_edge("alerts", "report")
    workflow.add_edge("report", END)

    return workflow.compile()


# ── Compiled graph singleton ──────────────────────────────────────────────────
graph = build_graph()


def run_analysis(
    ticker: str,
    company_name: str = "",
    analysis_depth: str = "standard",
    portfolio_positions: list | None = None,
    alert_thresholds: dict | None = None,
) -> MarketPulseState:
    """
    Run the full MarketPulse analysis pipeline for a given ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        company_name: Full company name (auto-resolved if empty)
        analysis_depth: "quick" | "standard" | "deep"
        portfolio_positions: Optional list of position dicts for portfolio analytics
        alert_thresholds: Optional overrides for alert evaluation thresholds

    Returns:
        Final MarketPulseState with all agent outputs.
    """
    ticker = normalize_ticker(ticker)
    if not validate_ticker(ticker):
        raise ValueError(f"Invalid ticker format: {ticker}")
    allowed = load_ticker_list(NASDAQ_TICKER_LIST_PATH)
    if not validate_ticker_against_list(ticker, allowed):
        raise ValueError(f"Ticker not found in NASDAQ list: {ticker}")

    # Auto-resolve company name if not provided
    if not company_name:
        try:
            import yfinance as yf
            info = yf.Ticker(ticker).info
            company_name = info.get("longName", ticker)
        except Exception:
            company_name = ticker

    initial_state: MarketPulseState = {
        "ticker": ticker,
        "company_name": company_name,
        "analysis_depth": analysis_depth,
        # News
        "raw_news": [],
        "news_fetched": False,
        # Sentiment
        "sentiment_scores": [],
        "overall_sentiment": "Neutral",
        "sentiment_confidence": 0.0,
        "sentiment_done": False,
        # Stock
        "stock_summary": {},
        "price_history": [],
        "stock_fetched": False,
        # Watchlist
        "watchlist": [],
        "watchlist_done": False,
        # Risk
        "risk_flags": [],
        "risk_level": "Medium",
        "key_insights": [],
        "risk_done": False,
        # Portfolio
        "portfolio_positions": portfolio_positions or [],
        "portfolio_summary": {},
        "portfolio_done": False,
        # Alerts
        "alerts": [],
        "alert_summary": "",
        "alert_counts": {},
        "has_critical_alerts": False,
        "alerts_done": False,
        "alert_thresholds": alert_thresholds or {},
        # Report
        "final_report": "",
        "report_path": None,
        "report_done": False,
        # Meta
        "messages": [],
        "error": None,
        "next_agent": "news",
    }

    print(f"\n{'='*60}")
    print(f"  MarketPulse Analysis: {company_name} ({ticker.upper()})")
    print(f"  Depth: {analysis_depth.capitalize()}")
    print(f"{'='*60}")

    final_state = graph.invoke(initial_state)

    write_json_log(
        {"ticker": ticker, "analysis_depth": analysis_depth, "state": final_state},
        LOG_OUTPUT_DIR,
        f"run_{ticker}",
    )

    print(f"\n{'='*60}")
    print(f"  ✅ Analysis Complete!")
    print(f"  Risk Level: {final_state.get('risk_level', 'N/A')}")
    print(f"  Sentiment: {final_state.get('overall_sentiment', 'N/A')}")
    if final_state.get("report_path"):
        print(f"  Report: {final_state['report_path']}")
    print(f"{'='*60}\n")

    return final_state
