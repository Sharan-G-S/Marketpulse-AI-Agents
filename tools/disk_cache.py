"""
MarketPulse — Persistent Disk & LRU Memory Cache
Stores quote responses on disk in reports/cache/ directory with TTL expiration.
"""

import json
import os
import time
from typing import Any, Optional

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "cache")


def get_disk_cache(key: str, max_age_seconds: int = 3600) -> Optional[Any]:
    """Retrieves cached json data from disk if within max_age_seconds."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    filepath = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(filepath):
        return None

    try:
        mtime = os.path.getmtime(filepath)
        if time.time() - mtime > max_age_seconds:
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def set_disk_cache(key: str, data: Any):
    """Saves json data to disk cache."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        filepath = os.path.join(CACHE_DIR, f"{key}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass
