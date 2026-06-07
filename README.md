# 📈 MarketPulse - Autonomous Financial Intelligence Agent

[![CI](https://github.com/Sharan-G-S/Marketpulse-AI-Agents/actions/workflows/ci.yml/badge.svg)](https://github.com/Sharan-G-S/Marketpulse-AI-Agents/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-green.svg)](https://python.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39%2B-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A **multi-agent autonomous AI system** that scrapes financial news, analyzes market sentiment, fetches real-time stock data, identifies investment risks, and generates professional investment intelligence reports — all orchestrated by **LangGraph**.



## 🎯 What It Does

Enter any stock ticker → 5 AI agents collaborate autonomously → Full investment report in ~60 seconds.

```
[News Agent] → [Stock Agent] → [Sentiment Agent] → [Risk Agent] → [Report Agent]
```



## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph StateGraph                          │
│                                                                 │
│  📰 News Agent   →   📈 Stock Agent                             │
│                           │                                     │
│                    🧠 Sentiment Agent                            │
│                           │                                     │
│                    ⚠️  Risk Analyst Agent                        │
│                           │                                     │
│                    📄 Report Generator                           │
│                           │                                     │
│                          END                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Role | Tools |
|-------|------|-------|
| 📰 **News Agent** | Fetches recent financial news | NewsAPI, mock fallback |
| 📈 **Stock Data Agent** | Real-time OHLCV + financials | yfinance |
| 🧠 **Sentiment Agent** | Per-article LLM sentiment scoring | LangChain + OpenAI/Gemini |
| ⚠️ **Risk Analyst Agent** | Cross-references data, flags risks | LangChain + LLM |
| 📄 **Report Agent** | Generates full markdown report | LangChain + LLM |



## ✨ Feature Suite (v2.0.0)

### Analytics Tools

| Module | Description |
|--------|-------------|
| `tools/risk_metrics.py` | Sharpe, Sortino, VaR 95%, Max Drawdown, Calmar ratios |
| `tools/portfolio_performance.py` | Position P&L, market value, weight %, best/worst performer |
| `tools/diversification_scorer.py` | HHI + sector entropy composite diversification score (A-F) |
| `tools/portfolio_rebalancer.py` | Target allocation rebalancer (BUY/SELL amounts & shares) |
| `tools/volume_indicators.py` | OBV, ADL, Chaikin Money Flow series and trend signals |
| `tools/earnings_surprise.py` | EPS/revenue surprise %, verdict tiers, multi-period trend |
| `tools/ma_crossover.py` | SMA/EMA series, Golden Cross & Death Cross detection |
| `tools/watchlist_alerts.py` | Price/RSI/volume threshold alerts for watchlists |
| `tools/news_digest.py` | Deduplication, sentiment ranking, Markdown digest |
| `tools/market_calendar.py` | Earnings dates, ex-dividends, US holiday overlay |
| `tools/data_quality.py` | OHLCV bar validation, quality scoring (0-100), issues report |
| `tools/indicator_signals.py` | RSI, MACD, MA, Bollinger signal wrappers |

### Streamlit Pages (15 total)

| Page | Feature |
|------|---------|
| `1_Report_History` | Past report browser |
| `3_Export_Data` | CSV data export |
| `4_Sector_Heatmap` | Sector heat map |
| `5_Compare_Stocks` | Multi-ticker comparison |
| `6_Screener` | Gainers/losers screener |
| `7_Sentiment_Trend` | Sentiment over time |
| `8_Risk_Dashboard` | Portfolio risk metrics |
| `9_Watchlist_Alerts` | Live price/RSI/volume alerts |
| `10_Indicators` | Technical indicator dashboard |
| `11_Portfolio_Performance` | Real-time P&L and weights |
| `12_News_Digest` | Deduplicated, ranked news digest |
| `13_Market_Calendar` | Earnings/dividend/holiday calendar |
| `14_Earnings_Surprise` | EPS surprise tracker |
| `15_MA_Crossover` | Golden/Death Cross detector |

### CLI Tools

```bash
# Run watchlist price/RSI alerts from the terminal
python tools/price_alerts_cli.py --tickers AAPL TSLA NVDA --pct 3.0
python tools/price_alerts_cli.py --tickers AAPL --json   # JSON output for pipelines
python tools/price_alerts_cli.py --help
```




## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key **or** Google Gemini API key
- NewsAPI key *(optional — mock data used if not set)*

### Installation

```bash
# 1. Clone
git clone https://github.com/Sharan-G-S/Marketpulse-AI-Agents.git
cd Marketpulse-AI-Agents

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env — add OPENAI_API_KEY or GOOGLE_API_KEY
```

### Run the Dashboard
```bash
streamlit run ui/app.py
```

### Run via CLI
```bash
python main.py --ticker AAPL
python main.py --ticker TSLA --depth deep
python main.py --ticker MSFT --company "Microsoft Corporation" --depth quick
```



## 📁 Project Structure

```
marketpulse-ai-agents/
│
├── agents/                     # Five autonomous AI agent modules
│   ├── news_agent.py           #   → Fetches financial news
│   ├── sentiment_agent.py      #   → LLM sentiment analysis
│   ├── stock_data_agent.py     #   → Real-time market data
│   ├── risk_analyst_agent.py   #   → Risk flags & insights
│   ├── report_agent.py         #   → Investment report generation
│   └── watchlist_agent.py      #   → Multi-ticker market overview
│
├── graph/
│   ├── state.py                # Shared TypedDict state schema
│   └── workflow.py             # LangGraph StateGraph definition
│
├── tools/
│   ├── stock_tools.py          # yfinance @tool wrappers
│   ├── news_tools.py           # NewsAPI @tool wrappers
│   ├── search_tools.py         # DuckDuckGo search tools
│   └── indicators.py           # RSI, MACD, Bollinger Bands, MAs
│
├── memory/
│   └── vector_store.py         # FAISS vector store for report history
│
├── config/
│   ├── settings.py             # Central environment config
│   ├── prompts.py              # Versioned prompt template registry
│   ├── logger.py               # Agent logger + execution timing
│   └── utils.py                # Formatting, validation helpers
│
├── ui/
│   ├── app.py                  # Main Streamlit dashboard
│   └── pages/
│       ├── 1_Report_History.py # Saved reports browser
│       └── 2_About.py          # Project info & tech stack
│
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   ├── test_agents.py          # Agent unit tests
│   ├── test_integration.py     # Pipeline integration tests
│   └── test_indicators.py      # Technical indicator tests
│
├── .github/workflows/ci.yml    # GitHub Actions CI (lint, test, security)
├── .streamlit/config.toml      # Streamlit dark theme config
├── docs/architecture.md        # System architecture documentation
├── main.py                     # CLI entry point
├── requirements.txt
└── .env.example
```



## 🔬 Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html

# Specific suite
pytest tests/test_indicators.py -v
pytest tests/test_integration.py -v
```



## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `openai` or `google` | `openai` |
| `LLM_MODEL` | Model name | `gpt-4o-mini` |
| `OPENAI_API_KEY` | OpenAI API key | *(required)* |
| `GOOGLE_API_KEY` | Google Gemini API key | *(optional)* |
| `NEWSAPI_KEY` | NewsAPI key | *(optional, mock if unset)* |
| `DEFAULT_PERIOD` | yfinance history period | `1mo` |
| `REPORT_OUTPUT_DIR` | Report save directory | `./reports` |
| `LOG_OUTPUT_DIR` | JSON run logs directory | `./logs` |
| `NASDAQ_TICKER_LIST_PATH` | Path to ticker list file | `./data/nasdaq_tickers.txt` |



## 👥 Team Contribution Guide

| Member | Ownership Area |
|--------|---------------|
| Member 1 | `agents/news_agent.py` + `tools/news_tools.py` |
| Member 2 | `agents/sentiment_agent.py` + `config/prompts.py` |
| Member 3 | `agents/stock_data_agent.py` + `tools/stock_tools.py` + `tools/indicators.py` |
| Member 4 | `agents/risk_analyst_agent.py` |
| Member 5 | `agents/report_agent.py` + `graph/workflow.py` |
| Member 6 | `ui/app.py` + `ui/pages/` + `tests/` |



## 🌟 Features

-  **5 autonomous AI agents** orchestrated by LangGraph StateGraph
-  **Real-time stock data** (price, market cap, PE, beta, 52W range)
-  **Interactive candlestick charts** with Plotly
-  **LLM sentiment analysis** per article + overall score
-  **Technical indicators** — RSI, MACD, Bollinger Bands, SMA/EMA
-  **Risk flagging** with Buy/Hold/Sell/Avoid recommendation
-  **Downloadable markdown reports**
-  **FAISS vector store** for report memory
-  **DuckDuckGo search** for supplemental research
-  **Multi-page Streamlit UI** with dark theme
-  **CLI support** with depth control
-  **GitHub Actions CI** — lint, test, security
-  **Mock news fallback** — works without NewsAPI key



## ⚠️ Disclaimer

MarketPulse is an **educational AI research tool** only.
It does **not** constitute financial advice. Always consult a qualified financial advisor.


## 🗺️ REST API Roadmap

Planned upgrades for a programmatic API layer:

- FastAPI service with `/analyze`, `/report/{id}`, and `/batch` endpoints
- Async background jobs with status polling
- JSON output format for reports + alert payloads
- API key auth + basic rate limiting


## 🧰 Troubleshooting

- Missing API keys: set `OPENAI_API_KEY` or `GOOGLE_API_KEY` in `.env`.
- NewsAPI errors: if `NEWSAPI_KEY` is unset, the system falls back to mock news.
- Invalid ticker: ticker format is validated and can be checked against the NASDAQ list if provided.
- No price history: yfinance may return empty data for illiquid or delisted symbols.
- Logs: structured JSON outputs are saved under `LOG_OUTPUT_DIR` after each run.



 *MIT License*
 *Team Project*

## Momentum Indicators

The `tools/momentum.py` module provides additional momentum analysis:

| Indicator | Function | Description |
|-----------|----------|-------------|
| Williams %R | `compute_williams_r` | Momentum oscillator (-100 to 0) |
| CCI | `compute_cci` | Commodity Channel Index |
| ROC | `compute_roc` | Rate of Change (price momentum %) |
| Summary | `get_momentum_summary` | All three indicators combined |


## Portfolio Summary

The `tools/portfolio_summary.py` module provides portfolio-level aggregation analytics:

| Metric / Feature | Function | Description |
|------------------|----------|-------------|
| Weighted Return | `weighted_portfolio_return` | Computes the weighted average annualised return of the portfolio |
| Weighted Volatility | `weighted_portfolio_volatility` | Computes the weighted average volatility (conservative upper bound) |
| Worst Drawdown Ticker | `worst_drawdown_ticker` | Identifies the holding with the worst max drawdown |
| Best Sharpe Ticker | `best_sharpe_ticker` | Identifies the holding with the highest Sharpe ratio |
| Portfolio Risk Label | `portfolio_risk_label` | Classifies the overall portfolio risk level (Low to Very High) |
| Portfolio Summary | `compute_portfolio_summary` | Aggregates all individual holding statistics into a portfolio summary dict |
| Markdown Dashboard | `format_portfolio_summary` | Formats the portfolio summary dict as a styled Markdown dashboard |


## Backtesting Simulator

The `tools/backtest_simulator.py` module provides backtesting analytics for trading strategies:

| Feature / Metric | Function | Description |
|------------------|----------|-------------|
| Run Crossover Backtest | `run_crossover_backtest` | Simulates trading a moving average crossover strategy and computes return, buy-and-hold benchmarks, win rates, drawdowns, and annualized Sharpe ratios |
| Format Backtest Report | `format_backtest_report` | Renders a comprehensive, styled Markdown report showing backtest performance and chronological trade ledgers |


## Portfolio Rebalancer

The `tools/portfolio_rebalancer.py` module provides target allocation rebalancing analytics:

| Feature / Metric | Function | Description |
|------------------|----------|-------------|
| Compute Rebalancing | `compute_portfolio_rebalancing` | Normalizes target weights, calculates position deviations (target vs actual), and generates BUY/SELL trade instructions (amounts & shares) and MAD tracking error |
| Format Rebalance Report | `format_rebalance_report` | Renders a beautiful, styled Markdown rebalancing dashboard report including current vs target allocation tables and recommended actions ledger |


## Volume Indicators

The `tools/volume_indicators.py` module provides volume-based indicator calculations and signal analysis:

| Feature / Metric | Function | Description |
|------------------|----------|-------------|
| Compute OBV | `compute_obv` | Calculates the On-Balance Volume cumulative series |
| Compute ADL | `compute_adl` | Calculates the Accumulation/Distribution Line cumulative series |
| Compute CMF | `compute_cmf` | Calculates the Chaikin Money Flow series over a period |
| Generate Volume Signals | `generate_volume_signals` | Analyzes volume indicators and produces aggregate trend signals |
