"""
Unit tests for tools/cache.py
"""

import time
from tools.cache import cache_ttl, clear_cache

call_count = 0


@cache_ttl(seconds=2)
def get_sample_data(param: str):
    global call_count
    call_count += 1
    return f"data_{param}_{call_count}"


def test_cache_ttl_returns_cached_result():
    global call_count
    clear_cache()
    call_count = 0

    res1 = get_sample_data("AAPL")
    assert res1 == "data_AAPL_1"
    assert call_count == 1

    # Second call within TTL should return cached value
    res2 = get_sample_data("AAPL")
    assert res2 == "data_AAPL_1"
    assert call_count == 1


def test_clear_cache():
    global call_count
    clear_cache()
    call_count = 0
    get_sample_data("TSLA")
    assert call_count == 1

    clear_cache()
    get_sample_data("TSLA")
    assert call_count == 2
