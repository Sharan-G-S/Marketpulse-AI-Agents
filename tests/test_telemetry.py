"""
Unit tests for config/telemetry.py
"""

from config.telemetry import get_metrics_summary, record_node_metric


def test_record_node_metric():
    entry = record_node_metric("news_agent", 0.45, status="success")
    assert entry["node"] == "news_agent"
    assert entry["duration_sec"] == 0.45

    summary = get_metrics_summary()
    assert summary["total_calls"] >= 1
    assert summary["avg_duration_sec"] > 0
