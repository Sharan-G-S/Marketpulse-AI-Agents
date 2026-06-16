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
    # portfolio summary
    "compute_portfolio_summary",
    "format_portfolio_summary",
    # momentum
    "compute_cci",
    "compute_roc",
    "compute_williams_r",
    "get_momentum_summary",
    # backtesting
    "format_backtest_report",
    "run_crossover_backtest",
    # portfolio rebalancing
    "compute_portfolio_rebalancing",
    "format_rebalance_report",
    # volume indicators
    "compute_obv",
    "compute_adl",
    "compute_cmf",
    "generate_volume_signals",
    # correlation
    "compute_correlation_matrix",
    "compute_rolling_correlation",
    "correlation_label",
    "format_correlation_report",
]

from .backtest_simulator import format_backtest_report, run_crossover_backtest
from .correlation import (
    compute_correlation_matrix,
    compute_rolling_correlation,
    correlation_label,
    format_correlation_report,
)
from .momentum import compute_cci, compute_roc, compute_williams_r, get_momentum_summary
from .portfolio_rebalancer import compute_portfolio_rebalancing, format_rebalance_report
from .portfolio_summary import compute_portfolio_summary, format_portfolio_summary
from .volume_indicators import compute_adl, compute_cmf, compute_obv, generate_volume_signals
