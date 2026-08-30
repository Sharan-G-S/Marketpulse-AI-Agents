"""
Unit tests for tools/concurrency_throttle.py and tools/http_pool.py
"""

from tools.concurrency_throttle import execute_with_throttle
from tools.http_pool import get_http_session


def test_get_http_session_singleton():
    s1 = get_http_session()
    s2 = get_http_session()
    assert s1 is s2


def test_execute_with_throttle():
    def sample_func(x, y):
        return x + y

    res = execute_with_throttle(sample_func, 10, 20)
    assert res == 30
