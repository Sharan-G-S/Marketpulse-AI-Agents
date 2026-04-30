"""
Agent Logger — Execution Timing & Structured Logging
Provides a decorator and utility class for tracking agent execution time,
success/failure, and producing a structured audit trail.
"""

from datetime import datetime
import functools
import logging
import time
from typing import Any, Callable, Dict, List

# ── Configure root logger ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)


class AgentLogger:
    """
    Structured logger for MarketPulse agents.
    Tracks timing, success/failure, and produces an audit trail.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"marketpulse.{agent_name}")
        self._entries: List[Dict[str, Any]] = []

    def log(self, message: str, level: str = "info", **kwargs):
        """Log a message with optional structured data."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.agent_name,
            "level": level.upper(),
            "message": message,
            **kwargs,
        }
        self._entries.append(entry)
        getattr(self.logger, level, self.logger.info)(message)

    def info(self, message: str, **kwargs):
        self.log(message, "info", **kwargs)

    def warning(self, message: str, **kwargs):
        self.log(message, "warning", **kwargs)

    def error(self, message: str, **kwargs):
        self.log(message, "error", **kwargs)

    @property
    def audit_trail(self) -> List[Dict[str, Any]]:
        return self._entries.copy()


def timed_agent(agent_name: str = None):
    """
    Decorator that wraps an agent node function to track execution time
    and log start/end to the shared state messages.

    Usage:
        @timed_agent("My Agent")
        def my_agent(state): ...
    """
    def decorator(func: Callable) -> Callable:
        name = agent_name or func.__name__.replace("_", " ").title()

        @functools.wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            start = time.perf_counter()
            logger = AgentLogger(name)
            logger.info(f"Starting {name}...")

            try:
                result = func(state)
                elapsed = time.perf_counter() - start
                logger.info(f"Completed in {elapsed:.2f}s", elapsed_seconds=round(elapsed, 2))

                # Append timing info to messages
                timing_msg = f"[{name}] Completed in {elapsed:.2f}s"
                existing = result.get("messages", [])
                return {**result, "messages": existing + [timing_msg]}

            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(f"Failed after {elapsed:.2f}s: {e}")
                raise

        return wrapper
    return decorator


# ── Global execution tracker ──────────────────────────────────────────────────
class ExecutionTracker:
    """Singleton that tracks the full pipeline execution history."""

    _instance = None
    _runs: List[Dict[str, Any]] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def record_run(self, ticker: str, state: Dict[str, Any], elapsed: float):
        self._runs.append({
            "ticker": ticker,
            "timestamp": datetime.utcnow().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "risk_level": state.get("risk_level", "N/A"),
            "sentiment": state.get("overall_sentiment", "N/A"),
            "report_generated": bool(state.get("final_report")),
        })

    @property
    def history(self) -> List[Dict[str, Any]]:
        return self._runs.copy()

    def clear(self):
        self._runs.clear()


execution_tracker = ExecutionTracker()
