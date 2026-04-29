# 📈 MarketPulse — Autonomous Financial Intelligence Agent

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

- ✅ **5 autonomous AI agents** orchestrated by LangGraph StateGraph
- ✅ **Real-time stock data** (price, market cap, PE, beta, 52W range)
- ✅ **Interactive candlestick charts** with Plotly
- ✅ **LLM sentiment analysis** per article + overall score
- ✅ **Technical indicators** — RSI, MACD, Bollinger Bands, SMA/EMA
- ✅ **Risk flagging** with Buy/Hold/Sell/Avoid recommendation
- ✅ **Downloadable markdown reports**
- ✅ **FAISS vector store** for report memory
- ✅ **DuckDuckGo search** for supplemental research
- ✅ **Multi-page Streamlit UI** with dark theme
- ✅ **CLI support** with depth control
- ✅ **GitHub Actions CI** — lint, test, security
- ✅ **Mock news fallback** — works without NewsAPI key



## ⚠️ Disclaimer

MarketPulse is an **educational AI research tool** only.
It does **not** constitute financial advice. Always consult a qualified financial advisor.



 *MIT License*
