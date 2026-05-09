# MarketPulse - Quick Reference

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the dashboard
streamlit run ui/app.py

# Run analysis from CLI
python main.py --ticker AAPL --depth standard
python main.py --ticker TSLA --depth deep
python main.py --ticker MSFT --depth quick
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/test_agents.py -v
pytest tests/test_indicators.py -v
```

## Lint Checks (must pass before PR)

```bash
isort --check-only .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

## Fix Lint Issues

```bash
isort .
```

## Analysis Depth Options

| Flag | Period | Use Case |
|------|--------|----------|
| `--depth quick` | 5 days | Fast scan |
| `--depth standard` | 1 month | Default analysis |
| `--depth deep` | 3 months | Comprehensive review |

## Environment Variables

Copy `.env.example` to `.env` and set:

```
OPENAI_API_KEY=sk-...
NEWSAPI_KEY=...         # optional, mock data used if unset
LLM_PROVIDER=openai    # or google
LLM_MODEL=gpt-4o-mini  # or gemini-1.5-flash
```

## Project Links

- Repository: https://github.com/Sharan-G-S/Marketpulse-AI-Agents
- Issues: https://github.com/Sharan-G-S/Marketpulse-AI-Agents/issues
- CI Status: https://github.com/Sharan-G-S/Marketpulse-AI-Agents/actions

---

## New Streamlit Pages (v1.5.0)

| Page | File | Description |
|------|------|-------------|
| Risk Dashboard | `ui/pages/8_Risk_Dashboard.py` | Sharpe, Sortino, Max Drawdown, VaR, Calmar |
| Watchlist Alerts | `ui/pages/9_Watchlist_Alerts.py` | Custom price/RSI/volume threshold alerts |
| Indicator Dashboard | `ui/pages/10_Indicators.py` | RSI, MACD, MA crossover, Bollinger Bands |

## Risk Metrics API

```python
from tools.risk_metrics import compute_risk_metrics

metrics = compute_risk_metrics(price_history, ticker="AAPL", risk_free_rate=0.05)
# Returns: ann_return, ann_volatility, sharpe, sortino,
#          max_drawdown, var_95, calmar, risk_label
```

## Watchlist Alerts API

```python
from tools.watchlist_alerts import DEFAULT_WATCHLIST_THRESHOLDS, evaluate_watchlist

alerts = evaluate_watchlist(entries, global_thresholds={"price_change_pct": 3.0})
# Supports: PRICE_CHANGE, PRICE_ABOVE, PRICE_BELOW, RSI_OVERBOUGHT,
#           RSI_OVERSOLD, VOLUME_SPIKE
```

## Indicator Signals API

```python
from tools.indicator_signals import format_indicator_table, overall_signal

signal = overall_signal(rsi=45.0, macd={"crossover": "Bullish"}, ma_signal_str="Golden Cross")
table  = format_indicator_table("AAPL", price, rsi, macd, ma_signal)
```

## Additional Environment Variables (v1.5.0)

```
RISK_FREE_RATE=0.05          # annual risk-free rate (default 5%)
RISK_DEFAULT_PERIOD=6mo      # default price history window for risk
WATCHLIST_PRICE_CHANGE_PCT=5.0   # price move alert threshold (%)
WATCHLIST_RSI_OVERBOUGHT=75.0    # RSI overbought level
WATCHLIST_RSI_OVERSOLD=25.0      # RSI oversold level
WATCHLIST_VOLUME_SPIKE=2.0       # volume × avg_volume alert ratio
SCREENER_TOP_N=5             # top-N movers shown per screener group
RSI_PERIOD=14                # RSI lookback window
MACD_FAST=12                 # MACD fast EMA period
MACD_SLOW=26                 # MACD slow EMA period
MACD_SIGNAL_PERIOD=9         # MACD signal line period
BB_PERIOD=20                 # Bollinger Bands period
BB_STD=2.0                   # Bollinger Bands std multiplier
```

## Running New Tests

```bash
pytest tests/test_risk_metrics.py -v
pytest tests/test_indicator_signals.py -v
pytest tests/ -v --tb=short    # full suite
```
