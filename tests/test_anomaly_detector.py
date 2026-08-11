"""
Unit tests for tools/anomaly_detector.py
"""

from tools.anomaly_detector import detect_price_anomalies


def test_detect_price_anomalies_clean():
    data = [
        {"close": 150.0},
        {"close": 152.0},
        {"close": 151.5},
    ]
    res = detect_price_anomalies(data)
    assert res["health_score"] == 100.0
    assert len(res["anomalies"]) == 0


def test_detect_price_anomalies_with_invalid():
    data = [
        {"close": 150.0},
        {"close": -5.0},
        {"close": 152.0},
    ]
    res = detect_price_anomalies(data)
    assert res["health_score"] < 100.0
    assert len(res["anomalies"]) >= 1
