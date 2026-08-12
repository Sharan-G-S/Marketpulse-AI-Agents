"""
MarketPulse — Enterprise Authorization & JWT Auth Middleware
Provides API key header authentication and token verification for enterprise endpoints.
"""

import hmac
import hashlib
from typing import Dict, Any


def authenticate_api_request(headers: Dict[str, str], required_key: str = "") -> Dict[str, Any]:
    """
    Validates API authorization headers for enterprise REST API requests.

    Args:
        headers: Request headers dictionary
        required_key: Expected API key token

    Returns:
        Dict with authenticated (True/False) and status message.
    """
    if not required_key:
        return {"authenticated": True, "message": "Development mode — auth bypassed"}

    auth_header = headers.get("Authorization") or headers.get("X-API-Key") or ""

    if not auth_header:
        return {"authenticated": False, "message": "Missing X-API-Key header"}

    token = auth_header.replace("Bearer ", "").strip()

    if hmac.compare_digest(token, required_key):
        return {"authenticated": True, "message": "Authorized enterprise session"}

    return {"authenticated": False, "message": "Invalid API Authorization key"}
