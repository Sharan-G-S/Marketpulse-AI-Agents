# MarketPulse — Architecture & Design

## Overview

MarketPulse is a **multi-agent autonomous financial intelligence system** built on
LangGraph and LangChain. It orchestrates five specialized AI agents through a
directed state graph, each responsible for one analytical step.

---

## Agent Graph

```
Inputs: ticker, company_name, analysis_depth
         │
         ▼
  ┌─────────────┐
  │  News Agent │  ← Fetches financial news via NewsAPI
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Stock Agent │  ← Fetches OHLCV, market data via yfinance
  └──────┬──────┘
         │
         ▼
  ┌──────────────────┐
  │ Sentiment Agent  │  ← LLM sentiment scoring per article
  └──────┬───────────┘
         │
         ▼
  ┌──────────────────┐
  │ Risk Analyst     │  ← Cross-references sentiment + market data
  └──────┬───────────┘
         │
         ▼
  ┌──────────────────┐
  │ Report Agent     │  ← Generates full markdown investment report
  └──────┬───────────┘
         │
        END
```

---

## Shared State

All agents communicate exclusively through `MarketPulseState` (TypedDict).
No agent calls another agent directly — all coordination is handled by LangGraph.

---

## LLM Interaction Points

| Agent            | LLM Task                              | Output Schema        |
|------------------|---------------------------------------|----------------------|
| Sentiment Agent  | Per-article sentiment classification  | `SentimentAnalysis`  |
| Risk Agent       | Risk flag generation + recommendation | `RiskAnalysis`       |
| Report Agent     | Full report in Markdown format        | `str` (StrOutputParser) |

---

## Extensibility

To add a new agent:
1. Create `agents/your_agent.py` with a function `(state) -> state`
2. Add it as a node in `graph/workflow.py`
3. Wire edges in `build_graph()`
4. Add output fields to `graph/state.py`

---

## Data Flow

```
NewsAPI ──────────────► raw_news[]
                              │
yfinance ─────────────► stock_summary{}
                              │
                        [Sentiment LLM]
                              │
                        sentiment_scores[]
                        overall_sentiment
                              │
                        [Risk LLM]
                              │
                        risk_flags[]
                        risk_level
                        key_insights[]
                              │
                        [Report LLM]
                              │
                        final_report (markdown)
                        report_path (saved file)
```
