"""
MarketPulse Configuration Settings
Loads and validates all environment variables and app constants.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")       # "openai" | "google"
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

# ── News ─────────────────────────────────────────────────────────────────────
NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
NEWS_MAX_ARTICLES: int = int(os.getenv("NEWS_MAX_ARTICLES", "10"))

# ── Stock Data ────────────────────────────────────────────────────────────────
DEFAULT_PERIOD: str = os.getenv("DEFAULT_PERIOD", "1mo")       # yfinance period
DEFAULT_INTERVAL: str = os.getenv("DEFAULT_INTERVAL", "1d")

# ── Memory / Vector Store ─────────────────────────────────────────────────────
VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./memory/faiss_index")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# ── Reporting ─────────────────────────────────────────────────────────────────
REPORT_OUTPUT_DIR: str = os.getenv("REPORT_OUTPUT_DIR", "./reports")
os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)

# ── Misc ──────────────────────────────────────────────────────────────────────
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
APP_TITLE: str = "MarketPulse — Autonomous Financial Intelligence Agent"
