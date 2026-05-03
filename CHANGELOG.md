# MarketPulse - Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- PDF export for investment reports
- Portfolio-level multi-ticker analysis
- Email alert integration for risk threshold breaches
- Historical report comparison view

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
