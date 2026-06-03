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

## [1.7.4] - 2026-05-15

### Added
- `tools/indicators.py` — Added `compute_stochastic_oscillator()` (%K/%D) and `compute_atr()` (Average True Range). Wired both into `get_all_indicators()`.
- `config/utils.py` — Added `format_large_number()` generic helper and `format_change_pct()` HTML color tags helper.
- `tools/stock_tools.py` — Added `free_cash_flow` to `get_financials()` output.

### Fixed
- `config/utils.py` — Fixed `format_volume()` negative value edge case.
- `agents/risk_analyst_agent.py` — Guarded `market_cap` string formatting against type errors by using `format_large_number()`.
- `agents/sentiment_agent.py` — Expanded `_BULLISH_KEYWORDS` and `_BEARISH_KEYWORDS` for better heuristic scoring.

### Updated
- `CONTRIBUTING.md` — Added Windows PowerShell virtualenv activation command `.\.venv\Scripts\Activate.ps1`.

---

## [1.7.3] - 2026-05-15

### Fixed
- `agents/portfolio_tracker.py` — `compute_position_pnl()` returned `pnl_pct = 0.0` when `avg_price = 0` (undefined return). Now returns `None`, consistent with `portfolio_performance.compute_position`.
- `config/utils.py` — `format_market_cap(0)` and `format_volume(0)` returned `"N/A"` due to falsy `if not cap` check. Fixed to `if cap is None`.
- `config/logger.py` — `ExecutionTracker._runs` was a mutable class-level attribute (shared across test runs). Now initialised on the singleton instance. Also fixed `write_json_log` to use `ensure_ascii=False` for readable UTF-8 output.
- `tools/search_tools.py` — `web_search_results()` parsed DuckDuckGo output with a fragile string splitter. Now tries JSON parsing first, then falls back to text splitting.
- `agents/sentiment_agent.py` — `score_articles()` missed ~30-40% of keyword matches because punctuation was not stripped before tokenizing. Fixed with `re.sub(r"[^\w\s]", " ", text)`.

### Added
- `tests/test_indicators.py` — Added `test_rsi_oversold_with_falling_prices` and `test_rsi_boundary_period_plus_one` to fill coverage gaps.

### Updated
- `tests/test_portfolio_tracker.py` — Updated `test_zero_avg_price` to assert `pnl_pct is None`.
- `CONTRIBUTING.md` — Added `pytest-asyncio` to dev install, Windows activation command, CHANGELOG checklist item, and CI tip.
- `docs/api_reference.md` — Bumped to v1.7.2; added `tools.news_tools` and `tools.csv_export` sections; added breaking-change callout for `pnl_pct / unrealised_pct = None`.
- `docs/architecture.md` — Updated to 8-node agent graph topology; added Known Limitations table.
- `graph/state.py` — Improved field comments; `portfolio_summary` is now `Optional[Dict]`; added Design Notes docstring.

---

## [1.7.2] - 2026-05-13

### Fixed
- `tools/news_digest.py` — `_jaccard()` returned `1.0` when both titles were empty, causing all subsequent blank-title articles to be deduped out silently. Fixed to return `0.0` (non-comparable).
- `tools/news_digest.py` — `_parse_date()` returned raw strings like `"bad"` for malformed dates instead of `"Unknown"`. Now validates extracted prefix with `datetime.strptime`.
- `tools/news_digest.py` — `digest_sentiment_summary()` called `max()` on all-zero counts when entries list was empty, returning an arbitrary key. Now returns `"Neutral"` explicitly for empty input.
- `tools/portfolio_performance.py` — `compute_position()` returned `unrealised_pct = 0.0` when `avg_cost = 0` (undefined/infinite return). Now returns `None` to avoid misleading display.
- `tools/portfolio_performance.py` — `compute_portfolio()` sort on `unrealised_pct` crashed with `TypeError` when any position had `avg_cost=0` (now `None`). Fixed sort key to `(pct or 0.0)`.
- `tools/ma_crossover.py` — `ma_crossover_summary()` early-return for empty price history was missing keys (`fast_value`, `slow_value`, `n_bars`, `ma_type`, etc.) causing `KeyError` in the MA Crossover UI page.

### Updated
- `tests/test_new_tools.py` — Updated `TestComputePosition.test_zero_avg_cost` to assert `unrealised_pct is None` (was `0.0`).
- `ui/pages/2_About.py` — Added **Version History** table covering v1.0.0–v1.7.2.

---

## [1.7.1] - 2026-05-13

### Fixed
- `tools/news_tools.py` — Added missing `fetch_news(ticker, max_results)` plain-function wrapper.
  Two Streamlit pages (`12_News_Digest`, `7_Sentiment_Trend`) imported it causing `ImportError`.
- `tools/sector_heatmap.py` — Changed `list[str]` type annotation to `List[str]` for Python <3.10 compatibility.
- `tools/price_alerts_cli.py` — Changed pipe-union `List[str] | None` to `Optional[List[str]]` for Python <3.10 compatibility; added `Optional` to typing imports.
- `tools/data_quality.py` — Fixed OHLC consistency checks firing spurious close/open warnings when `high < low` error already present; added negative volume validation.
- `tools/diversification_scorer.py` — Fixed `ZeroDivisionError` when all `market_value=0` (falls back to equal weighting); fixed `ValueError` from `max()` on empty `sector_weights` dict; added early-exit for empty portfolio.
- `tools/earnings_surprise.py` — Changed `tuple[float, float]` return annotation to `Tuple[float, float]` (typing module) for Python <3.10 compatibility; documented negative-estimated-EPS behavior.

---

## [1.7.0] - 2026-05-12

### Added
- `tools/diversification_scorer.py` — HHI-based portfolio diversification score (0-100, A-F grade): `compute_hhi()`, `sector_entropy()`, `score_diversification()` with actionable rebalancing suggestions.
- `tools/earnings_surprise.py` — EPS/revenue surprise tracker: 5-tier verdict (Strong Beat→Strong Miss), multi-period trend analysis, Markdown table formatter.
- `tools/ma_crossover.py` — Moving Average Crossover engine: SMA/EMA series, Golden/Death Cross detection, `ma_crossover_summary()` with current trend signal.
- `tools/data_quality.py` — OHLCV and stock summary data quality validator: per-bar OHLC consistency checks, 0-100 quality score, Markdown issue report.
- `tools/price_alerts_cli.py` — CLI alert scanner: argparse interface, ANSI colour output, JSON mode for CI pipelines, exit code 1 on critical alerts.
- `ui/pages/14_Earnings_Surprise.py` — Earnings Surprise Tracker page: CSV entry, per-ticker trend summary, results table, CSV download.
- `ui/pages/15_MA_Crossover.py` — MA Crossover Signals page: fast/slow period inputs, EMA toggle, colour-coded signal badges, crossover event tables.
- `docs/api_reference.md` — Comprehensive API reference for all 10 tool modules (function signatures, return types, schema docs).
- `tests/test_v17_tools.py` — 57 unit tests for all four new modules (all green).

### Fixed
- `agents/sentiment_agent.py` — Added missing `score_articles()` function (LLM-free keyword heuristic scorer). Two pages (`7_Sentiment_Trend`, `12_News_Digest`) were importing it causing `ImportError`.
- `tools/risk_metrics_helpers.py` — Fixed `TypeError: 'NoneType' * int` in `format_risk_table()` and `risk_metrics_to_dict()` when metric values are `None` (short price histories). Guard via `(value or 0.0)`.
- `config/settings.py` — Added 11 new env-var constants for portfolio, MA crossover, earnings surprise, and data quality feature modules.

### Refactored
- Added `_MODULE` and `_VERSION = "1.7.0"` metadata constants to all 5 new v1.7.0 tool modules for runtime introspection.

---

## [1.6.0] - 2026-05-11

### Added
- `tools/portfolio_performance.py` — Pure-Python portfolio P&L engine:
  `compute_position()` (MV, cost basis, unrealised P&L, weight %),
  `compute_portfolio()` (two-pass aggregation with best/worst performer),
  `top_holdings()`, `sector_allocation()`.
- `ui/pages/11_Portfolio_Performance.py` — Streamlit Portfolio Performance page:
  CSV-style position entry, live price fetch, P&L metric tiles, position
  breakdown table, top-holdings bar chart, CSV download.
- `tools/news_digest.py` — News digest formatter: Jaccard-based deduplication,
  sentiment-weighted ranking, DigestEntry builder, Markdown renderer,
  `digest_sentiment_summary()`.
- `ui/pages/12_News_Digest.py` — Streamlit News Digest page: full pipeline
  (fetch → deduplicate → rank → format), article cards, sentiment stats,
  Markdown download.
- `tools/market_calendar.py` — Market calendar tool: earnings/ex-dividend
  extraction from yfinance summaries, US market holiday list,
  `build_market_calendar()`, `format_calendar_markdown()`,
  `upcoming_earnings_list()`.
- `ui/pages/13_Market_Calendar.py` — Streamlit Market Calendar page: colour-coded
  event cards, earnings countdown table, full calendar DataFrame, Markdown download.
- `tests/test_new_tools.py` — 34 unit tests for portfolio_performance,
  news_digest, and market_calendar.

### Fixed
- `agents/alert_helpers.py` — Resolved `ImportError: cannot import name
  'AlertSeverity'` that caused 4 CI test failures across all Python versions.
  Replaced with correct `WatchlistTriggeredAlert` + string severity constants.
- `agents/screener_agent.py` — Fixed two bugs in breadth/screener logic:
  (1) `run_screener()` losers list sliced before filtering, silently producing
  fewer than top_n results; now filter-then-slice to match gainers pattern.
  (2) `screener_breadth()` all-flat breadth_label returned "Strong Advance"
  when advances==0 and declines==0 due to `0 >= 0*2` being True; added
  explicit zero guard.
- `tools/__init__.py` — Cleaned up multi-line import formatting and added
  usage comments for lazy-importable v1.4.0+ modules.

---

## [1.5.0] - 2026-05-09

### Added
- `tools/risk_metrics.py` — Portfolio risk engine: `compute_daily_returns()`,
  `annualised_return()`, `annualised_volatility()`, `sharpe_ratio()`,
  `sortino_ratio()`, `max_drawdown()`, `value_at_risk_95()`, `calmar_ratio()`,
  `risk_label()`, and `compute_risk_metrics()` full-bundle function.
- `tools/risk_metrics_helpers.py` — Risk display utilities: `sharpe_badge()`,
  `mdd_badge()`, `var_badge()`, `format_risk_table()`,
  `format_multi_risk_table()`, `risk_metrics_to_dict()`.
- `ui/pages/8_Risk_Dashboard.py` — New Streamlit Risk Dashboard: multi-ticker
  Sharpe/Sortino/Max Drawdown/VaR/Calmar comparison with per-ticker drill-down
  tabs, CSV and Markdown download buttons.
- `tools/watchlist_alerts.py` — Watchlist alert engine: six alert types
  (PRICE_CHANGE, PRICE_ABOVE, PRICE_BELOW, RSI_OVERBOUGHT, RSI_OVERSOLD,
  VOLUME_SPIKE), severity-sorted output, per-ticker threshold overrides.
- `ui/pages/9_Watchlist_Alerts.py` — New Streamlit Watchlist Alerts page:
  custom threshold controls, live scan, colour-coded alert cards, CSV export.
- `tools/indicator_signals.py` — Indicator signal helpers: `rsi_signal()`,
  `macd_signal()`, `ma_signal()`, `bollinger_signal()`, `overall_signal()`,
  `format_indicator_table()`, `format_multi_indicator_table()`.
- `ui/pages/10_Indicators.py` — New Streamlit Technical Indicator Dashboard:
  vote-based overall signal tiles, side-by-side comparison table,
  per-ticker tabs with RSI/MACD/MA/Bollinger Bands, raw data table.
- `tests/test_risk_metrics.py` — 28 unit tests for all risk metric functions.
- `tests/test_indicator_signals.py` — 24 unit tests for all signal helpers.

### Changed
- `config/settings.py` — Added 14 new env-var-backed constants for risk
  (RISK_FREE_RATE, RISK_DEFAULT_PERIOD, RISK_MAX_TICKERS), watchlist alerts
  (WATCHLIST_PRICE_CHANGE_PCT, WATCHLIST_RSI_OVERBOUGHT, WATCHLIST_RSI_OVERSOLD,
  WATCHLIST_VOLUME_SPIKE), screener (SCREENER_TOP_N, SCREENER_DEFAULT_UNIVERSE),
  and indicator parameters (RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
  BB_PERIOD, BB_STD).
- `docs/quickref.md` — Extended with v1.5.0 page table, API snippets for all
  three new modules, environment variable reference, and test commands.

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
\n## [1.7.5] - 2026-05-19\n### Added\n- VWAP Indicator\n### Fixed\n- Bug in get_all_indicators where empty closes would crash RSI\n\n## [1.7.6] - 2026-05-19\n### Added\n- OBV Indicator\n### Fixed\n- Bug in MACD empty closes check\n
## [1.7.7] - 2026-05-21
### Added
- Fibonacci Retracement Indicator in tools/fibonacci.py

## [1.7.8] - 2026-05-23
### Added
- Momentum Indicators module (Williams %R, CCI, ROC)
- Unit tests for all momentum indicators
### Fixed
- ROC period validation

## [1.7.9] - 2026-05-26
### Added
- `tools/portfolio_summary.py` — Portfolio-level aggregation module providing weighted portfolio returns, volatility estimation, best Sharpe/worst drawdown ticker identification, risk label classification, and Markdown dashboard formatting.
- `tests/test_portfolio_summary.py` — 17 unit tests verifying all portfolio summary calculations and edge cases.
### Fixed
- `tools/data_quality.py` — Updated duplicate date check to recognize `"timestamp"` alongside `"date"` and `"Date"`.
- `tools/momentum.py` — Wrapped `compute_roc` in `get_momentum_summary` inside a try-except block to gracefully handle ValueError exception.

## [1.8.0] - 2026-05-28
### Added
- `tools/backtest_simulator.py` — High-performance moving average crossover Backtesting Simulator providing transaction ledgers, cash/equity curves, win rates, maximum drawdowns, and annualized Sharpe ratios.
- `tests/test_backtest_simulator.py` — Complete unit test suite verifying all crossover backtesting strategies, statistics, and Markdown formats.
### Fixed
- `tools/risk_metrics.py` — Guarded `compute_daily_returns` against division-by-zero errors when a prior day's close price is `0.0`.
- `tools/diversification_scorer.py` — Hardened `score_diversification` against type conversions when `market_value` contains invalid/non-numeric strings.
- `tools/earnings_surprise.py` — Hardened consensus and reported EPS/revenue parsing against invalid or blank string values.
- `tools/watchlist_alerts.py` — Guarded volume spike ratio checks against type mismatch errors.
- `tools/fibonacci.py` — Resolved dictionary gotcha where `high`/`low` keys having a value of `None` caused TypeErrors instead of falling back to default prices.

## [1.9.0] - 2026-06-01
### Added
- `tools/portfolio_rebalancer.py` — Portfolio Allocation & Rebalancing Engine calculates position deviations and trade actions (BUY/SELL amounts and shares) to align with target allocations, including MAD tracking error and Markdown dashboard reports.
- `tests/test_portfolio_rebalancer.py` — Comprehensive unit test suite covering weight normalization, deviation calculations, trade recommendations, and markdown formatting.
### Fixed
- `tools/backtest_simulator.py` — Guarded against potential division by zero on zero-price and purchase price inside crossover trade evaluations.
- `tools/ma_crossover.py` — Added safety guards against zero or negative moving average periods in simple and exponential moving averages.
- `tools/risk_metrics.py` — Hardened `sharpe_ratio` and `sortino_ratio` calculations against empty return list input or zero/NaN volatilities.
- `tools/diversification_scorer.py` — Guarded `_count_score` against zero or negative capping parameters to prevent square-root or division faults.
- `tools/earnings_surprise.py` — Added tiny float `abs(estimated) < 1e-9` and NaN consensus guards in `compute_eps_surprise`.
- `tools/watchlist_alerts.py` — Hardened average volume spike checks with tiny float and NaN validations.
## [2.0.0] - 2026-06-03
### Added
- `tools/volume_indicators.py` — High-performance volume indicators module providing On-Balance Volume (OBV), Accumulation/Distribution Line (ADL), and Chaikin Money Flow (CMF) series and trend signal generation.
- `tests/test_volume_indicators.py` — Comprehensive unit test suite with 14 tests verifying calculations, zero division handling, invalid data handling, and trend signal logic.
