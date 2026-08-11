"""
Unit tests for config/security.py
"""

from config.security import redact_secrets, sanitize_ticker, validate_environment_security


def test_sanitize_ticker():
    assert sanitize_ticker("aapl") == "AAPL"
    assert sanitize_ticker("  tsla  ") == "TSLA"
    assert sanitize_ticker("AAPL;<script>") == "AAPL"
    assert sanitize_ticker("BRK.A") == "BRK.A"


def test_redact_secrets():
    raw = "Connecting with sk-1234567890abcdef1234567890 to LLM service"
    redacted = redact_secrets(raw)
    assert "[REDACTED_API_KEY]" in redacted
    assert "sk-1234567890abcdef1234567890" not in redacted


def test_validate_environment_security():
    res = validate_environment_security()
    assert "status" in res
    assert "sanitization_active" in res
    assert res["sanitization_active"] is True
