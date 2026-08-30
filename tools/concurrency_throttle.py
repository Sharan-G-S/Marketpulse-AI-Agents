"""
MarketPulse — Concurrency Throttle & Resource Governor
Limits concurrent worker threads for API network operations.
"""

import threading

_SEMAPHORE = threading.Semaphore(10)


def execute_with_throttle(func, *args, **kwargs):
    """Executes target function within a bounded concurrency semaphore guard."""
    with _SEMAPHORE:
        return func(*args, **kwargs)
