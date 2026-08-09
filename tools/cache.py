"""
MarketPulse — Data Caching Layer
In-memory & disk TTL caching system for yfinance price quotes and financial news.
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


def clear_cache():
    """Clears all cached responses."""
    global _CACHE
    _CACHE.clear()
