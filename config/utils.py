"""
Utility functions for MarketPulse — number formatting, text helpers,
ticker validation, and report export utilities.
"""

from datetime import datetime, timezone
import functools
import os
import re
from typing import Optional

# ── Number Formatting ─────────────────────────────────────────────────────────

def format_market_cap(cap: Optional[float]) -> str:
    """Format a market cap number into human-readable string."""
    if not cap:
        return "N/A"
    if cap >= 1e12:
        return f"${cap / 1e12:.2f}T"
    if cap >= 1e9:
        return f"${cap / 1e9:.2f}B"
    if cap >= 1e6:
        return f"${cap / 1e6:.2f}M"
    return f"${cap:,.0f}"


def format_volume(vol: Optional[int]) -> str:
    """Format trading volume into human-readable string."""
    if not vol:
        return "N/A"
    if vol >= 1e9:
        return f"{vol / 1e9:.2f}B"
    if vol >= 1e6:
        return f"{vol / 1e6:.1f}M"
    if vol >= 1e3:
        return f"{vol / 1e3:.1f}K"
    return str(vol)


def format_price(price: Optional[float], currency: str = "$") -> str:
    """Format a price with currency symbol."""
    if price is None:
        return "N/A"
    return f"{currency}{price:.2f}"


def format_percent(pct: Optional[float], show_sign: bool = True) -> str:
    """Format a percentage value with optional +/- sign."""
    if pct is None:
        return "N/A"
    sign = "+" if pct > 0 and show_sign else ""
    return f"{sign}{pct:.2f}%"


# ── Ticker Validation ─────────────────────────────────────────────────────────

def validate_ticker(ticker: str) -> bool:
    """
    Validate a stock ticker symbol.
    Valid: 1-5 uppercase letters, optionally with a dot (e.g., BRK.B).
    """
    pattern = r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$"
    return bool(re.match(pattern, ticker.strip().upper()))


def normalize_ticker(ticker: str) -> str:
    """Normalize a ticker input to uppercase, stripped of whitespace."""
    return ticker.strip().upper()


@functools.lru_cache(maxsize=2)
def load_ticker_list(path: str) -> set:
    """Load ticker symbols from a newline-delimited file if present."""
    if not path or not os.path.exists(path):
        return set()
    tickers = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            sym = line.strip().upper()
            if not sym or sym.startswith("#"):
                continue
            if validate_ticker(sym):
                tickers.add(sym)
    return tickers


def validate_ticker_against_list(ticker: str, allowed: set) -> bool:
    """Return True if list is empty or ticker exists in list."""
    if not allowed:
        return True
    return ticker in allowed


# ── Risk Color Coding ─────────────────────────────────────────────────────────

RISK_COLORS = {
    "Low":      "#48bb78",   # green
    "Medium":   "#f6ad55",   # orange
    "High":     "#fc8181",   # red
    "Critical": "#f56565",   # bright red
}

SENTIMENT_COLORS = {
    "Bullish":  "#48bb78",
    "Bearish":  "#fc8181",
    "Neutral":  "#a0aec0",
}


def get_risk_color(risk_level: str) -> str:
    return RISK_COLORS.get(risk_level, "#a0aec0")


def get_sentiment_color(sentiment: str) -> str:
    return SENTIMENT_COLORS.get(sentiment, "#a0aec0")


# ── Report Export ─────────────────────────────────────────────────────────────

def save_report(report_content: str, ticker: str, output_dir: str = "./reports") -> str:
    """
    Save a report to disk with a timestamped filename.

    Returns:
        Absolute path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{ticker.upper()}_{timestamp}_report.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)

    return os.path.abspath(filepath)


def list_saved_reports(output_dir: str = "./reports") -> list:
    """List all saved reports sorted by most recent first."""
    if not os.path.exists(output_dir):
        return []
    files = [f for f in os.listdir(output_dir) if f.endswith("_report.md")]
    files.sort(reverse=True)
    return [os.path.join(output_dir, f) for f in files]


# ── Text Utilities ─────────────────────────────────────────────────────────────

def truncate(text: str, max_len: int = 100, suffix: str = "...") -> str:
    """Truncate text to max_len characters."""
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def extract_ticker_from_text(text: str) -> Optional[str]:
    """
    Attempt to extract a stock ticker from free text.
    Looks for patterns like $AAPL or standalone uppercase words 1-5 chars.
    """
    # Look for $TICKER pattern first
    dollar_match = re.search(r"\$([A-Z]{1,5})", text.upper())
    if dollar_match:
        return dollar_match.group(1)
    # Look for standalone uppercase words
    words = re.findall(r"\b[A-Z]{2,5}\b", text.upper())
    return words[0] if words else None
