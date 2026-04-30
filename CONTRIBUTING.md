# Contributing to MarketPulse

Thank you for your interest in contributing to MarketPulse. This document outlines the process and standards for contributing to this project.

---

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/Sharan-G-S/Marketpulse-AI-Agents.git
cd Marketpulse-AI-Agents
```

### 2. Set Up the Development Environment

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
pip install -r requirements.txt
pip install isort flake8 flake8-bugbear pytest pytest-cov
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

---

## Development Workflow

### Branching Strategy

Use descriptive branch names following this convention:

- `feat/agent-name` - New agent or major feature
- `fix/issue-description` - Bug fix
- `style/module-name` - Code style or formatting changes
- `docs/section-name` - Documentation updates
- `test/test-name` - New or updated tests
- `ci/workflow-change` - CI/CD changes

### Making Changes

1. Create a feature branch from `main`
2. Make your changes in small, focused commits
3. Ensure all lint checks pass before pushing
4. Write or update tests for your changes
5. Open a Pull Request with a clear description

---

## Code Standards

### Import Ordering

All imports must be sorted using `isort` with the `black` profile:

```bash
isort .
```

Imports should follow this order:
1. Standard library imports
2. Third-party imports (langchain, langgraph, yfinance, etc.)
3. First-party imports (agents, graph, tools, memory, config)

### Linting

Run flake8 before every commit:

```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

Maximum line length is **120 characters**.

### Docstrings

All public functions and classes must have docstrings:

```python
def my_function(param: str) -> dict:
    """
    Brief one-line description.

    Args:
        param: Description of the parameter.

    Returns:
        Description of what is returned.
    """
```

---

## Testing

Run the full test suite before submitting a Pull Request:

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Specific module
pytest tests/test_agents.py -v
```

All new features must include corresponding unit tests. Aim for test coverage above 70% on new code.

---

## Agent Development Guide

To add a new agent to the pipeline:

### 1. Create the Agent Module

Create a new file in `agents/your_agent.py`:

```python
from graph.state import MarketPulseState


def your_agent(state: MarketPulseState) -> MarketPulseState:
    """
    Your Agent Node.

    Brief description of what this agent does.
    """
    ticker = state["ticker"]
    print(f"[Your Agent] Processing {ticker}...")

    # Your logic here

    return {
        **state,
        "messages": state.get("messages", []) + ["[Your Agent] Task complete."],
    }
```

### 2. Register in the Graph

Add your agent to `graph/workflow.py`:

```python
from agents.your_agent import your_agent

workflow.add_node("your_node", your_agent)
workflow.add_edge("previous_node", "your_node")
workflow.add_edge("your_node", "next_node")
```

### 3. Add State Fields

If your agent produces new data, add fields to `graph/state.py`:

```python
class MarketPulseState(TypedDict):
    # ... existing fields
    your_output: str
    your_done: bool
```

### 4. Export from Package

Add to `agents/__init__.py`:

```python
from .your_agent import your_agent
```

### 5. Write Tests

Add tests to `tests/test_agents.py` or create a new test file.

---

## Pull Request Checklist

Before opening a Pull Request, verify:

- [ ] All lint checks pass (`isort --check-only .` and `flake8 .`)
- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] New tests added for new functionality
- [ ] Docstrings added to all new public functions
- [ ] `README.md` updated if adding new features
- [ ] No hardcoded API keys or secrets
- [ ] No emojis in code comments or docstrings

---

## Project Structure Reference

See `README.md` for the full project structure. Key directories:

- `agents/` - Individual agent node functions
- `graph/` - LangGraph workflow and state schema
- `tools/` - LangChain tool wrappers
- `config/` - Configuration, prompts, utilities
- `tests/` - All test files
- `ui/` - Streamlit dashboard

---

## Reporting Issues

Use GitHub Issues to report bugs or request features. Include:

- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Relevant error messages or logs
