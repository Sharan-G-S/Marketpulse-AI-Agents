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


def should_continue(state: MarketPulseState) -> str:
    """
    After news + stock data are fetched in parallel,
    check if we have enough data to proceed with analysis.
    """
    if state.get("error") and not state.get("raw_news") and not state.get("stock_fetched"):
        return "report"
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
        [news] -> [stock] -> [watchlist] -> [sentiment] -> [risk] -> [portfolio?] -> [alerts] -> [report] -> END
    """
    workflow = StateGraph(MarketPulseState)

    workflow.add_node("news", news_agent)
    workflow.add_node("stock", stock_data_agent)
    workflow.add_node("watchlist", watchlist_agent)
    workflow.add_node("sentiment", sentiment_agent)
    workflow.add_node("risk", risk_analyst_agent)
    workflow.add_node("portfolio", portfolio_agent)
    workflow.add_node("alerts", alert_agent)
    workflow.add_node("report", report_agent)

    workflow.set_entry_point("news")

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
    """
    ticker = normalize_ticker(ticker)
    if not validate_ticker(ticker):
        raise ValueError(f"Invalid ticker format: {ticker}")

    # Fallback company resolution
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
        "raw_news": [],
        "news_fetched": False,
        "sentiment_scores": [],
        "overall_sentiment": "Neutral",
        "sentiment_confidence": 0.0,
        "sentiment_done": False,
        "stock_summary": {},
        "price_history": [],
        "stock_fetched": False,
        "watchlist": [],
        "watchlist_done": False,
        "risk_flags": [],
        "risk_level": "Medium",
        "key_insights": [],
        "risk_done": False,
        "portfolio_positions": portfolio_positions or [],
        "portfolio_summary": {},
        "portfolio_done": False,
        "alerts": [],
        "alert_summary": "",
        "alert_counts": {},
        "has_critical_alerts": False,
        "alerts_done": False,
        "alert_thresholds": alert_thresholds or {},
        "final_report": "",
        "report_path": None,
        "report_done": False,
        "messages": [],
        "error": None,
        "next_agent": "news",
    }

    final_state = graph.invoke(initial_state)

    try:
        write_json_log(
            {"ticker": ticker, "analysis_depth": analysis_depth, "state": final_state},
            LOG_OUTPUT_DIR,
            f"run_{ticker}",
        )
    except Exception:
        pass

    return final_state
