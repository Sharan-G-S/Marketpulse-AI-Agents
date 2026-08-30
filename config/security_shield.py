"""
MarketPulse — Security Input Sanitizer & XSS Shield
Strips malicious script tags, HTML tags, and command injection chars from user prompts.
"""

import html
import re


def sanitize_user_input(text: str) -> str:
    """
    Sanitizes string inputs against XSS and script injection.
    """
    if not isinstance(text, str):
        return ""

    # Escape HTML
    escaped = html.escape(text.strip())

    # Remove script tags or command separators
    cleaned = re.sub(r"[<>;|`$]", "", escaped)
    return cleaned[:500]
