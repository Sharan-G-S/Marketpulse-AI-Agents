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

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_OUTPUT_DIR: str = os.getenv("LOG_OUTPUT_DIR", "./logs")
os.makedirs(LOG_OUTPUT_DIR, exist_ok=True)

# ── Validation ───────────────────────────────────────────────────────────────
NASDAQ_TICKER_LIST_PATH: str = os.getenv("NASDAQ_TICKER_LIST_PATH", "./data/nasdaq_tickers.txt")

# ── Misc ──────────────────────────────────────────────────────────────────────
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
APP_TITLE: str = "MarketPulse — Autonomous Financial Intelligence Agent"

# ── Risk Metrics ──────────────────────────────────────────────────────────────
RISK_FREE_RATE: float = float(os.getenv("RISK_FREE_RATE", "0.05"))   # annual decimal
RISK_DEFAULT_PERIOD: str = os.getenv("RISK_DEFAULT_PERIOD", "6mo")
RISK_MAX_TICKERS: int = int(os.getenv("RISK_MAX_TICKERS", "5"))

# ── Watchlist Alerts ──────────────────────────────────────────────────────────
WATCHLIST_PRICE_CHANGE_PCT: float = float(os.getenv("WATCHLIST_PRICE_CHANGE_PCT", "5.0"))
WATCHLIST_RSI_OVERBOUGHT: float = float(os.getenv("WATCHLIST_RSI_OVERBOUGHT", "75.0"))
WATCHLIST_RSI_OVERSOLD: float = float(os.getenv("WATCHLIST_RSI_OVERSOLD", "25.0"))
WATCHLIST_VOLUME_SPIKE: float = float(os.getenv("WATCHLIST_VOLUME_SPIKE", "2.0"))

# ── Screener ──────────────────────────────────────────────────────────────────
SCREENER_TOP_N: int = int(os.getenv("SCREENER_TOP_N", "5"))
SCREENER_DEFAULT_UNIVERSE: str = os.getenv("SCREENER_DEFAULT_UNIVERSE", "builtin")

# ── Technical Indicators ──────────────────────────────────────────────────────
RSI_PERIOD: int = int(os.getenv("RSI_PERIOD", "14"))
MACD_FAST: int = int(os.getenv("MACD_FAST", "12"))
MACD_SLOW: int = int(os.getenv("MACD_SLOW", "26"))
MACD_SIGNAL: int = int(os.getenv("MACD_SIGNAL_PERIOD", "9"))
BB_PERIOD: int = int(os.getenv("BB_PERIOD", "20"))
BB_STD: float = float(os.getenv("BB_STD", "2.0"))
# ── Portfolio & Diversification ───────────────────────────────────────────────
PORTFOLIO_MAX_POSITIONS: int = int(os.getenv("PORTFOLIO_MAX_POSITIONS", "50"))
DIVERSIFICATION_CAP_POSITIONS: int = int(os.getenv("DIVERSIFICATION_CAP_POSITIONS", "20"))

# ── MA Crossover ──────────────────────────────────────────────────────────────
MA_FAST_PERIOD: int = int(os.getenv("MA_FAST_PERIOD", "50"))
MA_SLOW_PERIOD: int = int(os.getenv("MA_SLOW_PERIOD", "200"))
MA_USE_EMA: bool = os.getenv("MA_USE_EMA", "false").lower() == "true"

# ── Earnings Surprise ─────────────────────────────────────────────────────────
EARNINGS_STRONG_BEAT_PCT: float = float(os.getenv("EARNINGS_STRONG_BEAT_PCT", "5.0"))
EARNINGS_BEAT_PCT: float = float(os.getenv("EARNINGS_BEAT_PCT", "1.0"))
EARNINGS_MISS_PCT: float = float(os.getenv("EARNINGS_MISS_PCT", "-1.0"))

# ── Data Quality ──────────────────────────────────────────────────────────────
DQ_MIN_BARS: int = int(os.getenv("DQ_MIN_BARS", "5"))
DQ_MAX_CHANGE_PCT: float = float(os.getenv("DQ_MAX_CHANGE_PCT", "50.0"))
