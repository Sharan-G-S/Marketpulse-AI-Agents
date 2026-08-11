"""
MarketPulse — Security & Input Sanitization Engine
Provides input sanitization, secret redaction, and environment security validation.
"""

import re
from typing import Any, Dict


def sanitize_ticker(ticker: str) -> str:
    """Sanitizes ticker symbol input to prevent injection attacks."""
    if not isinstance(ticker, str):
        return ""
    # Strip HTML tags or script injection
    cleaned = re.sub(r"<[^>]*>", "", ticker)
    # Truncate at semicolon or special delimiters
    cleaned = cleaned.split(";")[0].split("&")[0]
    cleaned = re.sub(r"[^A-Z0-9.\-]", "", cleaned.strip().upper())
    return cleaned[:10]


def redact_secrets(text: str) -> str:
    """Redacts API keys and sensitive tokens from log messages."""
    if not isinstance(text, str):
        return text
    redacted = re.sub(r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]", text)
    redacted = re.sub(r"(AIzaSy[a-zA-Z0-9_\-]{30,})", "[REDACTED_GEMINI_KEY]", redacted)
    return redacted


def validate_environment_security() -> Dict[str, Any]:
    """Validates security posture and checks for active API key configuration."""
    from config.settings import GOOGLE_API_KEY, OPENAI_API_KEY
    has_openai = bool(OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here")
    has_google = bool(GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here")

    return {
        "status": "secure" if (has_openai or has_google) else "warning",
        "has_openai_key": has_openai,
        "has_google_key": has_google,
        "sanitization_active": True,
    }
