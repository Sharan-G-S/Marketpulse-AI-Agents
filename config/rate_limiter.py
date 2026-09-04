"""
MarketPulse — Request Rate Limiting Token Bucket Governor
Token bucket governor for throttling external API request frequencies.
"""

import time
from typing import Dict, Any

_BUCKETS: Dict[str, float] = {}


def check_rate_limit(client_id: str = "default", max_requests_per_minute: int = 60) -> bool:
    """
    Checks if client request is within allowed rate limit window.
    """
    now = time.time()
    last_req = _BUCKETS.get(client_id, 0.0)
    min_interval = 60.0 / max(1, max_requests_per_minute)

    if now - last_req >= min_interval:
        _BUCKETS[client_id] = now
        return True
    return False
