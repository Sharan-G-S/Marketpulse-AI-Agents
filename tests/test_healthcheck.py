"""
Unit tests for healthcheck.py
"""

from healthcheck import check_health


def test_check_health():
    assert check_health() is True
