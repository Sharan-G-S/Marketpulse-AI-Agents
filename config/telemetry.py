"""
MarketPulse — Production Telemetry & Metrics Tracer
Logs execution latencies, node durations, and request metrics in structured JSON format.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict

_METRICS_LOG = []


def record_node_metric(node_name: str, duration_seconds: float, status: str = "success") -> Dict[str, Any]:
    """
    Records telemetry metrics for a single agent node invocation.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node": node_name,
        "duration_sec": round(float(duration_seconds), 4),
        "status": status,
    }
    _METRICS_LOG.append(entry)
    return entry


def get_metrics_summary() -> Dict[str, Any]:
    """
    Returns aggregated metrics summary.
    """
    if not _METRICS_LOG:
        return {"total_calls": 0, "avg_duration_sec": 0.0}

    total_dur = sum(m["duration_sec"] for m in _METRICS_LOG)
    avg_dur = total_dur / len(_METRICS_LOG)

    return {
        "total_calls": len(_METRICS_LOG),
        "avg_duration_sec": round(avg_dur, 4),
        "metrics": _METRICS_LOG[-10:],
    }
