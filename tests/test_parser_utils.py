"""
Unit tests for agents/parser_utils.py
"""

from agents.parser_utils import clean_json_string, parse_llm_json_safe


def test_clean_json_string():
    raw = "```json\n{\"sentiment\": \"Bullish\"}\n```"
    assert clean_json_string(raw) == '{"sentiment": "Bullish"}'


def test_parse_llm_json_safe_valid():
    raw = '{"status": "ok", "score": 0.8}'
    fallback = {"status": "error"}
    res = parse_llm_json_safe(raw, fallback)
    assert res["status"] == "ok"
    assert res["score"] == 0.8


def test_parse_llm_json_safe_invalid_fallback():
    raw = "This is not valid json"
    fallback = {"status": "fallback"}
    res = parse_llm_json_safe(raw, fallback)
    assert res["status"] == "fallback"
