# MarketPulse — API Reference

Complete reference for all public tool functions (v1.7.2).

> **v1.7.2 changes:** `compute_position.unrealised_pct` and
> `compute_position_pnl.pnl_pct` now return `None` instead of `0.0`
> when `avg_cost / avg_price` is 0 (gifted/bonus shares — percentage
> return is undefined). Update any callers that assumed a `float`.

---

## tools.risk_metrics

```python
from tools.risk_metrics import compute_risk_metrics

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `compute_daily_returns` | `(history: List[Dict])` | `List[float]` |
| `annualised_return` | `(returns: List[float])` | `float` |
| `annualised_volatility` | `(returns: List[float])` | `float` |
| `sharpe_ratio` | `(returns, rfr=0.05)` | `float` |
| `sortino_ratio` | `(returns, rfr=0.05)` | `float` |
| `max_drawdown` | `(history: List[Dict])` | `float` |
| `value_at_risk_95` | `(returns: List[float])` | `float` |
| `calmar_ratio` | `(returns, history)` | `float` |
| `risk_label` | `(sharpe, mdd, vol)` | `"Low"\|"Moderate"\|"High"\|"Very High"` |
| `compute_risk_metrics` | `(history, ticker, rfr=0.05)` | `Dict` |

---

## tools.portfolio_performance

```python
from tools.portfolio_performance import compute_portfolio

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `compute_position` | `(position, current_price, total_mv=0)` | `PositionResult` |
| `compute_portfolio` | `(positions, price_map)` | `PortfolioSummary` |
| `top_holdings` | `(summary, n=5)` | `List[PositionResult]` |
| `sector_allocation` | `(positions, sector_map=None)` | `Dict[str, float]` |

---

## tools.diversification_scorer

```python
from tools.diversification_scorer import score_diversification

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `compute_hhi` | `(weights: List[float])` | `float` (0-1) |
| `sector_entropy` | `(sector_weights: Dict[str, float])` | `float` (0-1) |
| `score_diversification` | `(positions, sector_map, weights, sector_weights)` | `DiversificationResult` |

**`DiversificationResult` keys:** `score`, `grade` (A-F), `sector_score`, `concentration_score`, `count_score`, `hhi`, `n_sectors`, `n_positions`, `dominant_sector`, `dominant_weight_pct`, `interpretation`, `suggestions`.

---

## tools.earnings_surprise

```python
from tools.earnings_surprise import compute_earnings_surprise, earnings_trend

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `compute_eps_surprise` | `(reported, estimated)` | `(pct, abs)` |
| `eps_verdict` | `(surprise_pct)` | `str` |
| `revenue_verdict` | `(surprise_pct)` | `str \| None` |
| `overall_verdict` | `(eps_v, rev_v)` | `str` |
| `compute_earnings_surprise` | `(record: EarningsRecord)` | `SurpriseResult` |
| `compute_earnings_history` | `(records: List[EarningsRecord])` | `List[SurpriseResult]` |
| `earnings_trend` | `(results: List[SurpriseResult])` | `Dict` |
| `format_earnings_table` | `(results)` | `str` (Markdown) |

**Verdict tiers:** Strong Beat 🚀 / Beat 🟢 / Meet ⚪ / Miss 🟡 / Strong Miss 🔴

---

## tools.ma_crossover

```python
from tools.ma_crossover import ma_crossover_summary

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `compute_sma` | `(prices, period)` | `List[Optional[float]]` |
| `compute_ema` | `(prices, period)` | `List[Optional[float]]` |
| `detect_crossovers` | `(fast_series, slow_series)` | `List[CrossoverEvent]` |
| `extract_closes` | `(price_history)` | `List[float]` |
| `ma_crossover_summary` | `(history, fast=50, slow=200, use_ema=False)` | `Dict` |

---

## tools.watchlist_alerts

```python
from tools.watchlist_alerts import evaluate_watchlist

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `evaluate_watchlist_entry` | `(entry, thresholds=None)` | `List[AlertRecord]` |
| `evaluate_watchlist` | `(entries, global_thresholds=None)` | `List[AlertRecord]` |
| `watchlist_alert_summary` | `(alerts)` | `Dict` |

**Alert types:** `PRICE_CHANGE`, `PRICE_ABOVE`, `PRICE_BELOW`, `RSI_OVERBOUGHT`, `RSI_OVERSOLD`, `VOLUME_SPIKE`

---

## tools.news_digest

```python
from tools.news_digest import build_digest_entries, format_news_digest_markdown

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `deduplicate_articles` | `(articles, threshold=0.6)` | `List[Article]` |
| `rank_articles` | `(articles, top_n=10)` | `List[Article]` |
| `build_digest_entries` | `(articles)` | `List[DigestEntry]` |
| `format_news_digest_markdown` | `(ticker, entries, max=8)` | `str` |
| `digest_sentiment_summary` | `(entries)` | `Dict` |

---

## tools.market_calendar

```python
from tools.market_calendar import build_market_calendar, format_calendar_markdown

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `extract_earnings_date` | `(stock_summary)` | `str \| None` |
| `extract_ex_dividend_date` | `(stock_summary)` | `str \| None` |
| `build_ticker_events` | `(ticker, stock_summary)` | `List[MarketEvent]` |
| `build_market_calendar` | `(summaries, holidays, days_ahead)` | `List[MarketEvent]` |
| `format_calendar_markdown` | `(events)` | `str` |
| `upcoming_earnings_list` | `(summaries, days_ahead=30)` | `List[Dict]` |

---

## tools.data_quality

```python
from tools.data_quality import validate_price_history, validate_stock_summary

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `validate_bar` | `(bar: Dict, index: int)` | `List[Issue]` |
| `validate_price_history` | `(history, min_bars=5)` | `ValidationReport` |
| `validate_stock_summary` | `(summary: Dict)` | `ValidationReport` |
| `format_validation_report` | `(report, label="Data")` | `str` |

**ValidationReport keys:** `valid`, `score` (0-100), `issues`, `errors`, `warnings`

---

## tools.indicator_signals

```python
from tools.indicator_signals import format_indicator_table, overall_signal

```

| Function | Signature | Returns |
|----------|-----------|---------|
| `rsi_signal` | `(rsi)` | `str` |
| `macd_signal` | `(macd: Dict)` | `str` |
| `ma_signal` | `(ma_signal_str)` | `str` |
| `bollinger_signal` | `(bb: Dict, price)` | `str` |
| `overall_signal` | `(rsi, macd, ma_str)` | `"🟢 Bullish"\|"🔴 Bearish"\|"⚪ Neutral"` |
| `format_indicator_table` | `(ticker, price, rsi, macd, ma, bb)` | `str` |
| `format_multi_indicator_table` | `(entries)` | `str` |

---

## tools.news_tools

```python
from tools.news_tools import fetch_news
```

| Function | Signature | Returns |
|----------|-----------|------------|
| `fetch_financial_news` | `(ticker: str, max_results: int = 10)` → `@tool` | `List[Dict]` |
| `get_company_news` | `(company: str, max_results: int = 10)` → `@tool` | `List[Dict]` |
| `fetch_news` | `(ticker: str, max_results: int = 10)` | `List[Dict]` |

> **`fetch_news`** is a plain Python function (not a LangChain `@tool`).
> Use it when importing directly in Streamlit pages or scripts where
> `@tool` overhead is unwanted.  It shares the same NewsAPI integration
> and mock-data fallback as `fetch_financial_news`.

**Article dict keys:** `title`, `description`, `url`, `publishedAt`, `source`

---

## tools.csv_export

```python
from tools.csv_export import export_portfolio_csv, save_csv_to_disk
```

| Function | Signature | Returns |
|----------|-----------|------------|
| `export_portfolio_csv` | `(positions: List[Dict])` | `str` (CSV) |
| `export_watchlist_csv` | `(watchlist: List[Dict])` | `str` (CSV) |
| `export_alerts_csv` | `(alerts: List[Dict])` | `str` (CSV) |
| `save_csv_to_disk` | `(csv_content, prefix, output_dir="./reports")` | `str` (path) |
| `export_summary_csv` | `(portfolio_result, watchlist, alerts)` | `Dict[str, str]` |
