"""
MarketPulse — Security Response Headers & Content Security Policy (CSP)
Provides standard HTTP security headers for production deployment.
"""

from typing import Dict


def get_security_headers() -> Dict[str, str]:
    """Returns production HTTP security response headers."""
    return {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
