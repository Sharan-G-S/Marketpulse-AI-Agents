"""
MarketPulse — Earnings Call Transcript Sentiment & Guidance Summarizer
Analyzes executive sentiment tone, revenue guidance outlook, and management Q&A tone.
"""

from typing import Any, Dict


def analyze_transcript_tone(transcript_text: str) -> Dict[str, Any]:
    """
    Analyzes executive tone and guidance direction from earnings call transcript text.

    Args:
        transcript_text: Raw transcript text excerpt

    Returns:
        Dict with tone_sentiment, guidance_outlook, confidence, and key_topics.
    """
    if not transcript_text or not isinstance(transcript_text, str):
        return {"tone_sentiment": "Neutral", "guidance_outlook": "Stable", "confidence": 0.5}

    text_lower = transcript_text.lower()

    bull_count = sum(text_lower.count(w) for w in ["record", "growth", "expansion", "exceed", "strong", "raising guidance"])
    bear_count = sum(text_lower.count(w) for w in ["headwind", "decline", "unsettled", "lowering", "cautious", "pressure"])

    if bull_count > bear_count:
        tone = "Optimistic / Bullish"
        guidance = "Raised / Positive"
    elif bear_count > bull_count:
        tone = "Cautious / Bearish"
        guidance = "Lowered / Downside"
    else:
        tone = "Neutral / Balanced"
        guidance = "Unchanged / Stable"

    return {
        "tone_sentiment": tone,
        "guidance_outlook": guidance,
        "bullish_keywords": bull_count,
        "bearish_keywords": bear_count,
    }
