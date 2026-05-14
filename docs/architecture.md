# MarketPulse — Architecture & Design

## Overview

MarketPulse is a **multi-agent autonomous financial intelligence system** built on
LangGraph and LangChain. It orchestrates eight specialized AI agents through a
directed state graph, each responsible for one analytical step.

---

## Agent Graph (v1.7.0)

```
Inputs: ticker, company_name, analysis_depth
         │
         ▼
  ┌─────────────┐  ┌──────────────┐
  │  News Agent │  │  Stock Agent │  ← Run in parallel (fan-out)
  └──────┬──────┘  └──────┬───────┘
         └────────┬────────┘
                  ▼
  ┌───────────────────┐
  │  Watchlist Agent  │  ← Evaluates threshold alerts from stock data
  └──────────┬────────┘
             ▼
  ┌──────────────────┐
  │ Sentiment Agent  │  ← LLM (or heuristic fallback) per-article scoring
  └──────┬───────────┘
         ▼
  ┌──────────────────┐
  │  Risk Analyst    │  ← Cross-references sentiment + market data
  └──────┬───────────┘
         ▼
  ┌──────────────────┐
  │ Portfolio Agent  │  ← P&L, sector allocation, diversification
  └──────┬───────────┘
         ▼
  ┌──────────────────┐
  │  Alert Engine    │  ← Structured alerts (CRITICAL/WARNING/INFO)
  └──────┬───────────┘
         ▼
  ┌──────────────────┐
  │  Report Agent    │  ← Generates full Markdown investment report
  └──────┬───────────┘
         │
        END
```

---

## Shared State

All agents communicate exclusively through `MarketPulseState` (TypedDict in
`graph/state.py`). No agent calls another agent directly — all coordination
is handled by LangGraph conditional edges.

---

## LLM Interaction Points

| Agent            | LLM Task                              | Output Schema           |
|------------------|---------------------------------------|-------------------------|
| Sentiment Agent  | Per-article sentiment classification  | `SentimentAnalysis`     |
| Risk Agent       | Risk flag generation + recommendation | `RiskAnalysis`          |
| Report Agent     | Full report in Markdown format        | `str` (StrOutputParser) |

> **Heuristic fallback:** If no LLM API key is set, `sentiment_agent` falls back
> to the keyword-based `score_articles()` heuristic scorer (no LLM required).

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
                        [Sentiment LLM / heuristic]
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
                        [Portfolio Tracker]
                              │
                        portfolio_summary{}
                              │
                        [Alert Engine]
                              │
                        alerts[]
                        has_critical_alerts
                              │
                        [Report LLM]
                              │
                        final_report (markdown)
                        report_path (saved file)
```

---

## Known Limitations

| Issue | Workaround |
|-------|------------|
| Circular import: `agents/__init__.py` → `alert_engine` → `graph.state` → `graph.__init__` → `workflow` → `agents.alert_engine` | Test files use `importlib.util.spec_from_file_location` to load agent modules directly, bypassing `__init__.py` |
| CI requires `OPENAI_API_KEY` or `GOOGLE_API_KEY` only for LLM tests | Pure-Python tools are tested without any API key |
| `asyncio_mode = "auto"` in pyproject.toml requires `pytest-asyncio` installed | Add `pytest-asyncio` to dev dependencies (see CONTRIBUTING.md) |
