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
