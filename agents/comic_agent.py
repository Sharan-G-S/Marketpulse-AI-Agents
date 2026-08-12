"""
Comic Agent Storyteller for MarketPulse
Synthesizes market analysis into structured graphic novel comic panels.
"""

from typing import Any, Dict, List


def generate_comic_storyboard(state: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generates a 4-panel comic storyboard narrative from MarketPulseState.

    Returns:
        List of panel dicts with 'panel_number', 'title', 'narrative', 'dialogue', and 'sound_effect'.
    """
    ticker = state.get("ticker", "ASSET").upper()
    cname = state.get("company_name", ticker)
    sent = state.get("overall_sentiment", "Neutral")
    risk = state.get("risk_level", "Medium")

    return [
        {
            "panel": "PANEL 1",
            "title": "THREAT DETECTED!",
            "narrative": f"Agent MarketPulse zeroes in on {cname} ({ticker}).",
            "dialogue": f"Scanning news feeds for {ticker}... Found active market signals!",
            "sound_effect": "BEEP! BEEP!",
        },
        {
            "panel": "PANEL 2",
            "title": "SENTIMENT RECON!",
            "narrative": "LLM Sentiment Agent analyzes article velocity.",
            "dialogue": f"Overall sentiment rating confirmed as {sent.upper()}!",
            "sound_effect": "WHOOSH!",
        },
        {
            "panel": "PANEL 3",
            "title": "RISK EVALUATION!",
            "narrative": "Risk Analyst Agent scans downside volatility.",
            "dialogue": f"Watch out! Risk assessment level is {risk.upper()}!",
            "sound_effect": "KAPOW!",
        },
        {
            "panel": "PANEL 4",
            "title": "EXECUTIVE DECISION!",
            "narrative": "The Multi-Agent Committee delivers final verdict.",
            "dialogue": f"Mission complete for {ticker}! Report synthesized successfully.",
            "sound_effect": "BAM!",
        },
    ]
