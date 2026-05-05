# MarketPulse - Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- PDF export for investment reports
- Email alert integration for risk threshold breaches
- Historical report comparison view

---

## [1.4.0] - 2026-05-05

### Added
- `tools/price_history_export.py` — OHLCV price history serialiser:
  `enrich_ohlcv()` adds daily_change, daily_change_pct, typical_price, and
  range columns; `export_price_history_csv()` and `export_price_history_json()`
  produce download-ready output; `price_history_stats()` computes period
  high/low, avg close, avg volume, best/worst day.
- `agents/screener_agent.py` — Gainers & Losers screener: 45-ticker default
  universe, `classify_mover()`, `mover_emoji()`, `run_screener()` ranking top-N
  gainers/losers/volatile/flat groups, and `screener_breadth()` advance-decline
  ratio computation.
- `tools/screener_helpers.py` — Screener display utilities: per-group Markdown
  tables, full screener report, breadth summary card, and flat dicts for
  DataFrame display.
- `ui/pages/6_Screener.py` — New Streamlit Screener page: customisable ticker
  universe, progress-bar scan, four metric tiles, tabbed mover groups, and
  full Markdown report download.
- `tools/sentiment_trend.py` — Sentiment trend engine: `group_by_date()`,
  `build_sentiment_trend()` daily aggregation, `simulate_trend_from_snapshot()`
  with deterministic LCG jitter, `trend_direction()` half-period comparison,
  and `trend_summary_text()` narrative generator.
- `ui/pages/7_Sentiment_Trend.py` — New Streamlit Sentiment Trend page: line
  chart of avg_score, bar chart of article breakdown, trend direction metric,
  narrative insight card, and CSV download.

---

## [1.3.0] - 2026-05-04

### Added
- `tools/sector_heatmap.py` — Sector aggregation engine: `compute_heat_score()`
  (weighted 50% price, 30% RSI, 20% breadth), `aggregate_sector()`,
  `build_sector_heatmap()` returning sectors sorted hottest-first, and
  `get_top_and_bottom_sectors()` helper.
- `tools/heatmap_helpers.py` — Heatmap display utilities: `heat_score_emoji()`,
  `momentum_badge()`, `format_heatmap_table()` (Markdown), `format_heatmap_summary()`
  (breadth narrative), and `heatmap_to_dicts()` for DataFrame/CSV output.
- `ui/pages/4_Sector_Heatmap.py` — New Streamlit page: live sector heatmap with
  customisable ticker universe, colour-coded heat score table, breadth metrics,
  summary narrative, and Markdown download.
- `agents/comparison_agent.py` — Stock Comparison Agent: five-dimension composite
  scoring (momentum 25%, valuation 20%, technical 25%, stability 15%, 52W range
  15%), `compare_tickers()` ranking function, `score_label()` classifier.
- `agents/comparison_helpers.py` — Comparison display utilities: `score_bar()`,
  `score_emoji()`, `label_badge()`, `format_comparison_table()`,
  `format_rankings_summary()`, `format_score_breakdown_table()`.
- `ui/pages/5_Compare_Stocks.py` — New Streamlit page: 2–5 ticker comparison
  with winner banner, metric tiles, fundamentals table, score breakdown,
  medal-ranked summary, and Markdown download buttons.
- `tests/test_sector_heatmap.py` — 31 unit tests covering all public functions
  in the sector heatmap module.
- `tests/test_comparison_agent.py` — 42 unit tests covering all scoring
  functions, `compute_composite_score()`, and `compare_tickers()`.

### Fixed
- `agents/alert_engine.py` — Repaired corrupted `return` statement in
  `alert_agent()` where escaped `\n` sequences were stored as literals,
  causing a `SyntaxError` on Python 3.12.

---

## [1.2.0] - 2026-05-03

### Added
- `agents/alert_helpers.py` — Alert formatting utilities: severity sorting,
  grouping by level, per-alert Markdown rendering with severity icons, and
  a full grouped digest builder (`format_alert_digest`).
- `agents/alert_engine.py` — Extended with class-based multi-ticker rule
  engine: `WatchlistAlertType` enum, `AlertRule` dataclass, `WatchlistTriggeredAlert`
  dataclass, and `WatchlistAlertEngine` with `evaluate()` and
  `with_default_rules()` factory; complements the existing function-based
  LangGraph agent evaluator.
- `tools/csv_export.py` — CSV serialisation for portfolio positions, watchlist
  entries, and alert records; supports in-memory strings (Streamlit download)
  and timestamped disk export via `save_csv_to_disk()`.
- `ui/pages/3_Export_Data.py` — New Streamlit sidebar page: one-click CSV
  downloads for portfolio, watchlist, and alert data from the current session.

### Changed
- `agents/watchlist_agent.py` — Integrated `WatchlistAlertEngine` post-scan;
  enriches watchlist entries with `rsi` and `rsi_signal` fields; stores
  `watchlist_alerts` and `alert_digest` in shared state; price history period
  extended from `5d` to `1mo` for accurate RSI computation.

---

## [1.1.0] - 2025-04-30

### Added
- `pyproject.toml` with isort, flake8, and pytest configuration
- `setup.cfg` with flake8 per-file-ignores for tests and UI modules
- `CONTRIBUTING.md` with full development guide and agent authoring walkthrough
- `LICENSE` file (MIT)
- `CHANGELOG.md` to track version history

### Fixed
- CI lint job: replaced black (Python 3.12.5 incompatible) with isort-only check
- Applied `isort --profile black` across all 28 Python source files
- Flake8 now runs on Python 3.11 for guaranteed CI compatibility

### Changed
- CI workflow updated to use Python 3.11 for lint and security jobs
- README rewritten with no emoji characters, plain ASCII diagram for architecture

---

## [1.0.0] - 2025-04-28

### Added
- Initial five-agent LangGraph pipeline: News, Stock, Sentiment, Risk, Report
- `graph/state.py` - Shared TypedDict state schema for all agents
- `graph/workflow.py` - LangGraph StateGraph with conditional routing
- `agents/news_agent.py` - NewsAPI financial news fetcher with mock fallback
- `agents/stock_data_agent.py` - yfinance real-time and historical data agent
- `agents/sentiment_agent.py` - LLM-powered per-article sentiment classifier
- `agents/risk_analyst_agent.py` - Risk flag generator with Buy/Hold/Sell/Avoid recommendation
- `agents/report_agent.py` - Markdown investment report generator with file export
- `agents/watchlist_agent.py` - Multi-ticker comparative market overview agent
- `tools/stock_tools.py` - LangChain tool wrappers for yfinance
- `tools/news_tools.py` - LangChain tool wrappers for NewsAPI
- `tools/search_tools.py` - DuckDuckGo web search tools
- `tools/indicators.py` - RSI, MACD, Bollinger Bands, SMA/EMA computation
- `memory/vector_store.py` - FAISS vector store for report persistence and retrieval
- `config/settings.py` - Central environment variable configuration
- `config/prompts.py` - Versioned prompt template registry
- `config/logger.py` - Agent logger with execution timing and audit trail
- `config/utils.py` - Number formatting, ticker validation, and export utilities
- `ui/app.py` - Streamlit dark-themed dashboard with Plotly candlestick charts
- `ui/pages/1_Report_History.py` - Saved reports browser page
- `ui/pages/2_About.py` - Project info and tech stack overview page
- `main.py` - CLI entry point with depth control argument
- `tests/conftest.py` - Shared pytest fixtures
- `tests/test_agents.py` - Unit tests for all agent nodes
- `tests/test_integration.py` - Pipeline integration tests
- `tests/test_indicators.py` - Technical indicator unit tests
- `.github/workflows/ci.yml` - GitHub Actions CI with lint, test, security jobs
- `.streamlit/config.toml` - Streamlit dark theme configuration
- `docs/architecture.md` - System architecture documentation
