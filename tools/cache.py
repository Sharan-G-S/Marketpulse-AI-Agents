"""
MarketPulse — Data Caching Layer
In-memory & disk TTL caching system with automatic stale entry cleaner.
"""

from functools import wraps
import time

_CACHE = {}


def cache_ttl(seconds: int = 300):
    """
    Decorator for caching function responses in memory for a given TTL (in seconds).
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__name__, str(args), str(sorted(kwargs.items())))
            now = time.time()
            if key in _CACHE:
                result, timestamp = _CACHE[key]
                if now - timestamp < seconds:
                    return result

            result = func(*args, **kwargs)
            _CACHE[key] = (result, now)
            return result

        return wrapper

    return decorator


def evict_stale_cache(max_age_seconds: int = 3600):
    """Removes all cache entries older than max_age_seconds."""
    global _CACHE
    now = time.time()
    stale_keys = [k for k, (_, ts) in _CACHE.items() if now - ts > max_age_seconds]
    for k in stale_keys:
        del _CACHE[k]
    return len(stale_keys)


def clear_cache():
    """Clears all cached responses."""
    global _CACHE
    _CACHE.clear()
