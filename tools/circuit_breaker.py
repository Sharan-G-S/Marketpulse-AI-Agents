"""
MarketPulse — Circuit Breaker & Resiliency Pattern
Prevents cascading API failures by tripping an open circuit state when external services fail repeatedly.
"""

from functools import wraps
import time
from typing import Any, Callable


class CircuitBreakerOpenException(Exception):
    """Raised when a call is attempted on an open circuit breaker."""
    pass


class CircuitBreaker:
    """
    Circuit Breaker state machine: CLOSED -> OPEN -> HALF-OPEN
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_state_change = time.time()

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            if self.state == "OPEN":
                if now - self.last_state_change > self.recovery_timeout:
                    self.state = "HALF-OPEN"
                    self.last_state_change = now
                else:
                    raise CircuitBreakerOpenException(f"Circuit for '{func.__name__}' is OPEN.")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    self.last_state_change = now
                return result
            except Exception as e:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    self.last_state_change = now
                raise e

        return wrapper
