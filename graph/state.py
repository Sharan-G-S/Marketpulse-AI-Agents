"""
MarketPulse — Shared State Schema

This TypedDict is the single source of truth passed between all
agents in the LangGraph workflow. Every agent reads from and writes
back to this state object.

Design notes
------------
- All *_done booleans are set to True by the corresponding agent on success.
  They let downstream agents know whether their dependency has completed.
- `portfolio_summary` may contain `pnl_pct = None` for zero-cost positions
  (gifted/bonus shares) where the percentage return is undefined.  Callers
  must handle None before formatting as a percentage string.
- `messages` uses Annotated[…, operator.add] so LangGraph merges lists from
  parallel branches rather than overwriting them.
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
    portfolio_positions: List[Dict[str, Any]]    # [{ticker, quantity, avg_price, sector?}]
    portfolio_summary: Optional[Dict[str, Any]]  # None until portfolio_agent runs
    portfolio_done: bool

    # ── Alert Engine Output ──────────────────────────────────────────────────
    alerts: List[Dict[str, Any]]         # Structured alert payloads
    alert_summary: str                   # Human-readable summary
    alert_counts: Dict[str, int]         # {"CRITICAL": n, "WARNING": n, "INFO": n}
    has_critical_alerts: bool
    alerts_done: bool

    # ── Alert Configuration ──────────────────────────────────────────────────
    alert_thresholds: Dict[str, Any]     # Optional overrides for alert thresholds

    # ── Report Agent Output ───────────────────────────────────────────────────
    final_report: str                    # Markdown-formatted investment report
    report_path: Optional[str]           # Saved file path (None if save disabled)
    report_done: bool

    # ── Orchestration ─────────────────────────────────────────────────────────
    messages: Annotated[List[str], operator.add]   # Agent log messages (auto-merged)
    error: Optional[str]                           # Set on unrecoverable agent error
    next_agent: str                                # Supervisor routing target
