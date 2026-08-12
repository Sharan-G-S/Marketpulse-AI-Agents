"""
Unit tests for new analytics tools (esg_scorer, dark_pool_tracker, transcript_analyzer, macro_stress_test)
"""

from tools.dark_pool_tracker import detect_dark_pool_activity
from tools.esg_scorer import evaluate_esg_score
from tools.macro_stress_test import run_macro_stress_test
from tools.transcript_analyzer import analyze_transcript_tone


def test_evaluate_esg_score():
    res = evaluate_esg_score("AAPL")
    assert "total_esg_score" in res
    assert res["ticker"] == "AAPL"


def test_detect_dark_pool_activity():
    res = detect_dark_pool_activity(current_volume=3000000, avg_volume=1000000)
    assert res["is_anomaly"] is True
    assert res["volume_ratio"] == 3.0


def test_analyze_transcript_tone():
    text = "We reported record quarterly revenue growth exceeding management guidance."
    res = analyze_transcript_tone(text)
    assert "Bullish" in res["tone_sentiment"]


def test_run_macro_stress_test():
    res = run_macro_stress_test(total_value=100000.0, beta=1.2)
    assert len(res["scenarios"]) == 3
    assert res["starting_value"] == 100000.0
