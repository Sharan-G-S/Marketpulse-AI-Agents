"""
MarketPulse — Multi-Layer Cache Manager & Disk Cleanup Helper
Manages cache stats and purges expired memory/disk keys.
"""

from typing import Dict
from tools.cache import _CACHE, clear_cache, evict_stale_cache


def get_cache_statistics() -> Dict[str, int]:
    """Returns memory cache metrics."""
    return {
        "active_cache_entries": len(_CACHE),
    }


def purge_all_caches() -> int:
    """Purges all active cache items."""
    count = len(_CACHE)
    clear_cache()
    return count
