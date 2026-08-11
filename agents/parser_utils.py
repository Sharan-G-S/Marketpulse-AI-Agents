"""
MarketPulse — Agent Parser Utilities & Schema Healing
Provides resilient JSON parsing, markdown codeblock cleaning, and fallback dict recovery.
"""

import json
import re
from typing import Any, Dict


def clean_json_string(raw_text: str) -> str:
    """Strips markdown codeblock fences ```json ... ``` from raw LLM text."""
    if not isinstance(raw_text, str):
        return ""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def parse_llm_json_safe(raw_text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely parses JSON string from LLM output with fallback recovery.
    """
    cleaned = clean_json_string(raw_text)
    if not cleaned:
        return fallback

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Heuristic fix: add missing closing brace or quote if truncated
        try:
            if not cleaned.endswith("}"):
                cleaned += "}"
            return json.loads(cleaned)
        except Exception:
            return fallback
