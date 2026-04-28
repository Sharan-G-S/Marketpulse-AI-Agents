# 📈 MarketPulse — Autonomous Financial Intelligence Agent

> **Multi-Agent AI System** powered by **LangGraph** + **LangChain**  
> Analyzes stocks using autonomous AI agents: news scraping, sentiment analysis, market data, risk assessment, and report generation.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                        │
│                                                                 │
│  [News Agent] ──> [Stock Agent] ──> [Sentiment Agent]           │
│                                           │                     │
│                                    [Risk Analyst Agent]         │
│                                           │                     │
│                                    [Report Generator]           │
│                                           │                     │
│                                         END                     │
└─────────────────────────────────────────────────────────────────┘
```

### Agents

| Agent | Responsibility | Tools Used |
|-------|---------------|------------|
| 📰 **News Agent** | Fetches recent financial news | NewsAPI |
| 📈 **Stock Data Agent** | Real-time & historical market data | yfinance |
| 🧠 **Sentiment Agent** | LLM-powered news sentiment analysis | LangChain + OpenAI/Gemini |
| ⚠️ **Risk Analyst Agent** | Cross-references data, flags risks | LangChain + LLM |
| 📄 **Report Agent** | Generates investment intelligence report | LangChain + LLM |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-team/marketpulse-ai-agents.git
cd marketpulse-ai-agents
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required API keys:
- **OpenAI** or **Google Gemini** — for LLM (sentiment, risk, reporting)
- **NewsAPI** *(optional)* — for live news; mock data used if not set

### 5. Run the Streamlit Dashboard
```bash
streamlit run ui/app.py
```

### 6. Or Run via CLI
```bash
python main.py --ticker AAPL
python main.py --ticker TSLA --depth deep
python main.py --ticker MSFT --company "Microsoft Corporation" --depth quick
```

---

## 📁 Project Structure

```
marketpulse-ai-agents/
│
├── agents/                     # Individual AI agent modules
│   ├── news_agent.py           # Fetches financial news articles
│   ├── sentiment_agent.py      # LLM-based sentiment analyzer
│   ├── stock_data_agent.py     # Real-time market data fetcher
│   ├── risk_analyst_agent.py   # Risk assessment & insights
│   └── report_agent.py         # Investment report generator
│
├── graph/                      # LangGraph workflow
│   ├── state.py                # Shared state schema (TypedDict)
│   └── workflow.py             # Graph definition & compilation
│
├── tools/                      # LangChain @tool wrappers
│   ├── stock_tools.py          # yfinance tools
│   └── news_tools.py           # NewsAPI tools
│
├── memory/                     # Vector store (future RAG features)
│
├── config/
│   └── settings.py             # Central config from env vars
│
├── ui/
│   └── app.py                  # Streamlit dashboard
│
├── tests/
│   └── test_agents.py          # Unit tests (pytest)
│
├── docs/                       # Documentation
├── reports/                    # Auto-generated analysis reports
│
├── main.py                     # CLI entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🔬 Running Tests

```bash
pytest tests/ -v
```

---

## 🤝 Team Contribution Guide

| Member | Suggested Ownership |
|--------|---------------------|
| Member 1 | `agents/news_agent.py` + `tools/news_tools.py` |
| Member 2 | `agents/sentiment_agent.py` |
| Member 3 | `agents/stock_data_agent.py` + `tools/stock_tools.py` |
| Member 4 | `agents/risk_analyst_agent.py` |
| Member 5 | `agents/report_agent.py` + `graph/workflow.py` |
| Member 6 | `ui/app.py` + `tests/` |

---

## 🛠️ Tech Stack

- **LangGraph** — Multi-agent state machine orchestration
- **LangChain** — LLM chains, prompt templates, tool wrappers
- **OpenAI GPT-4o / Google Gemini** — LLM backbone
- **yfinance** — Free stock market data
- **NewsAPI** — Financial news articles
- **Streamlit** — Interactive dashboard UI
- **Plotly** — Candlestick charts & visualizations
- **FAISS** — Vector store for future memory features

---

## 📊 Features

- ✅ Real-time stock data (price, market cap, PE ratio, beta, 52W range)
- ✅ Interactive candlestick price chart
- ✅ LLM-powered news sentiment analysis (Bullish/Bearish/Neutral)
- ✅ Automated risk flag detection
- ✅ AI-generated investment insights
- ✅ Full markdown investment report (downloadable)
- ✅ CLI + Streamlit UI support
- ✅ Supports OpenAI and Google Gemini
- ✅ Mock news data for development (no API key required)

---

## ⚠️ Disclaimer

MarketPulse is an AI research tool for **educational purposes only**.  
It does **not** constitute financial advice. Always consult a qualified financial advisor before making investment decisions.

---

*Built with ❤️ using LangGraph + LangChain*
