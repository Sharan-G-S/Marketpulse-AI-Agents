from .news_tools import fetch_financial_news, fetch_top_headlines
from .search_tools import (
    search_analyst_ratings,
    search_company_background,
    web_search,
    web_search_results,
)
from .stock_tools import calculate_price_change, get_financials, get_price_history, get_stock_summary

# ── v1.4.0+ modules (lazy-importable via tools.<module>) ─────────────────────
# These are NOT imported at package level to avoid pulling in heavy deps
# on every `import tools`. Import them directly, e.g.:
#   from tools.risk_metrics import compute_risk_metrics
#   from tools.portfolio_performance import compute_portfolio
#   from tools.news_digest import build_digest_entries
#   from tools.market_calendar import build_market_calendar

__all__ = [
    # stock data
    "get_stock_summary",
    "get_price_history",
    "get_financials",
    "calculate_price_change",
    # news
    "fetch_financial_news",
    "fetch_top_headlines",
    # search
    "web_search",
    "web_search_results",
    "search_analyst_ratings",
    "search_company_background",
]
