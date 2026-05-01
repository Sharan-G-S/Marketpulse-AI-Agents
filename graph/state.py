"""
MarketPulse — Shared State Schema

This TypedDict is the single source of truth passed between all
agents in the LangGraph workflow. Every agent reads from and writes
back to this state object.
"""

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class MarketPulseState(TypedDict):
    """Shared state that flows through the entire agent graph."""

    # ── Input ─────────────────────────────────────────────────────────────────
    ticker: str                          # e.g. "AAPL", "TSLA"
    company_name: str                    # e.g. "Apple Inc."
    analysis_depth: str                  # "quick" | "standard" | "deep"

    # ── News Agent Output ─────────────────────────────────────────────────────
    raw_news: List[Dict[str, Any]]       # List of {title, url, publishedAt, source}
    news_fetched: bool

    # ── Sentiment Agent Output ────────────────────────────────────────────────
    sentiment_scores: List[Dict[str, Any]]   # [{title, sentiment, score, reasoning}]
    overall_sentiment: str                   # "Bullish" | "Bearish" | "Neutral"
    sentiment_confidence: float              # 0.0 – 1.0
    sentiment_done: bool

    # ── Stock Data Agent Output ───────────────────────────────────────────────
    stock_summary: Dict[str, Any]        # {current_price, high, low, volume, pe_ratio, ...}
    price_history: List[Dict[str, Any]]  # [{date, open, high, low, close, volume}]
    stock_fetched: bool

    # ── Watchlist Agent Output ────────────────────────────────────────────────
    watchlist: List[Dict[str, Any]]      # [{ticker, price, change_pct, trend, ...}]
    watchlist_done: bool

    # ── Risk Analyst Agent Output ─────────────────────────────────────────────
    risk_flags: List[str]                # Human-readable risk warnings
    risk_level: str                      # "Low" | "Medium" | "High" | "Critical"
    key_insights: List[str]              # Bullet-point insights
    risk_done: bool

    # ── Portfolio Tracker Output ─────────────────────────────────────────────
    portfolio_positions: List[Dict[str, Any]]  # [{ticker, quantity, avg_price, sector?}]
    portfolio_summary: Dict[str, Any]          # Computed portfolio analytics
    portfolio_done: bool

    # ── Alert Engine Output ──────────────────────────────────────────────────
    alerts: List[Dict[str, Any]]         # Structured alert payloads
    alert_summary: str                   # Human-readable summary
    alert_counts: Dict[str, int]         # Severity counts
    has_critical_alerts: bool
    alerts_done: bool

    # ── Alert Configuration ──────────────────────────────────────────────────
    alert_thresholds: Dict[str, Any]     # Optional overrides for alert thresholds

    # ── Report Agent Output ───────────────────────────────────────────────────
    final_report: str                    # Markdown-formatted investment report
    report_path: Optional[str]           # Saved file path
    report_done: bool

    # ── Orchestration ─────────────────────────────────────────────────────────
    messages: Annotated[List[str], operator.add]   # Agent log messages
    error: Optional[str]
    next_agent: str                      # Supervisor routing target
