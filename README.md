# 💥 MarketPulse AI — Worldwide Autonomous Multi-Agent Financial Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LLM-LangChain-green.svg)](https://github.com/langchain-ai/langchain)
[![UI Theme](https://img.shields.io/badge/UI-Claude_Dark_%26_Comic_PopArt-ffde59.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-564_Passing-success.svg)](https://docs.pytest.org/)

**MarketPulse AI** is a world-class, enterprise-grade financial intelligence platform featuring **19 specialized interactive subpages** and a **7-Agent LangGraph StateGraph pipeline**. It orchestrates autonomous AI agents to collect financial news, fetch real-time market quotes, perform per-article LLM sentiment scoring, analyze downside risk flags, compute Efficient Frontier portfolio weights, and deliver publication-grade investment reports in both **Claude Warm Dark Theme** and **Comic Pop-Art Graphic Novel UI**!

---

## 💥 Visual Themes & UI Previews

### 💥 Comic / Graphic Novel Financial Intelligence Mode (Page 16)
![MarketPulse Comic UI Dashboard](docs/images/comic_dashboard.jpg)

### 🧡 Main Dashboard (Claude Warm Dark Theme)
![MarketPulse Main Dashboard](docs/images/dashboard_claude.jpg)

### 📊 Stock Screener & Asset Comparison Matrix
![MarketPulse Stock Screener](docs/images/screener_claude.jpg)

---

## 📑 19 Interactive Subpages Overview

1. **Main Dashboard (`ui/app.py`)**: Central multi-agent graph executor & OHLC stock price history charts.
2. **`1_Report_History.py`**: Executive investment report archives.
3. **`2_About.py`**: LangGraph workflow architecture.
4. **`3_Export_Data.py`**: Export financial metrics as JSON/CSV.
5. **`4_Sector_Heatmap.py`**: Market sector heatmap visualizer.
6. **`5_Compare_Stocks.py`**: Side-by-side asset comparison & correlation matrix.
7. **`6_Screener.py`**: Quantitative filter stock screener.
8. **`7_Sentiment_Trend.py`**: Historical sentiment momentum trends.
9. **`8_Risk_Dashboard.py`**: Quantitative risk analytics (Sharpe, Sortino, VaR).
10. **`9_Watchlist_Alerts.py`**: Price target & RSI limits alerts.
11. **`10_Indicators.py`**: Technical indicators (RSI, MACD, Bollinger, Stochastic, ATR, VWAP, OBV, Fibonacci).
12. **`11_Portfolio_Performance.py`**: Portfolio holdings P&L and weight tracker.
13. **`12_News_Digest.py`**: Real-time financial news stream.
14. **`13_Market_Calendar.py`**: Economic data release calendar.
15. **`14_Earnings_Surprise.py`**: Historical EPS beat/miss trends.
16. **`15_MA_Crossover.py`**: Moving average crossover signals.
17. **`16_Comic_Dashboard.py`**: Graphic novel financial intelligence dashboard.
18. **`17_Global_Macro_Regime.py`**: World market index scanner (S&P 500, FTSE 100, Nikkei, Nifty) & Forex matrix.
19. **`18_Institutional_Flows.py`**: Dark pool order flow & block trade volume anomaly tracker.
20. **`19_Monte_Carlo_Simulator.py`**: 10,000-Path stochastic Geometric Brownian Motion simulator & 95% VaR visualizer.

*(Detailed documentation available in [`docs/page_directory.md`](docs/page_directory.md)).*

---

## 🛡️ Production Resilience & Security

- **ZeroDivision & NaN Safeguards**: Fixed division by zero in price change, Sharpe ratio, max drawdown, and position metrics.
- **NoneType Cost Basis Handling**: NoneType safety guards in portfolio performance trackers.
- **Security Input XSS Shield**: Sanitization of input strings against XSS script injection and command execution.
- **Zero Warnings Pytest Suite**: 100% warning-free test execution across 564 unit and integration tests.

---

## 🚀 Quickstart Guide

```bash
git clone https://github.com/Sharan-G-S/Marketpulse-AI-Agents.git
cd marketpulse-ai-agents
pip install -r requirements.txt
streamlit run ui/app.py
```

---

## 🧪 Test Suite Verification

Run the full pytest suite:
```bash
python -m pytest
```

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
