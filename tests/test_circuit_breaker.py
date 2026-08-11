"""
Unit tests for tools/circuit_breaker.py
"""

import pytest
import time
from tools.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException


def test_circuit_breaker_trips_open():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1.0)

    @cb
    def failing_fn():
        raise ValueError("API Error")

    with pytest.raises(ValueError):
        failing_fn()
    assert cb.state == "CLOSED"

    with pytest.raises(ValueError):
        failing_fn()
    assert cb.state == "OPEN"

    with pytest.raises(CircuitBreakerOpenException):
        failing_fn()
