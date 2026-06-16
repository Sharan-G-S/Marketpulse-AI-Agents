"""
Trade Signal Aggregation Engine for MarketPulse.

Combines signals from RSI, MACD, Bollinger Bands, MA Crossover,
and Volume Indicators into a unified directional signal with
a numeric strength score and confidence label.

No LLM required — rule-based signal fusion.
"""

from typing import Any, Dict, List, Optional

# ── Signal scoring weights ────────────────────────────────────────────────────

_WEIGHTS = {
    "rsi":     1.0,
    "macd":    1.5,
    "ma":      1.5,
    "bb":      1.0,
    "volume":  1.0,
    "stoch":   1.0,
}


# ── Core aggregation ──────────────────────────────────────────────────────────


def aggregate_signals(  # noqa: C901
    rsi: Optional[float] = None,
    macd: Optional[Dict[str, Any]] = None,
    ma_signal: Optional[str] = None,
    bb: Optional[Dict[str, Any]] = None,
    current_price: Optional[float] = None,
    volume_signal: Optional[str] = None,
    stochastic: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Aggregate individual technical indicator signals into a composite direction.

    Each indicator casts a weighted bull/bear vote.  The net weighted score
    determines the overall direction:
        score > +0.5 → Bullish
        score < -0.5 → Bearish
        otherwise   → Neutral

    Args:
        rsi:           RSI value (0–100).
        macd:          MACD dict with keys 'macd', 'signal', 'crossover'.
        ma_signal:     MA crossover string (e.g. 'Golden Cross (Bullish)').
        bb:            Bollinger Bands dict with keys 'upper', 'lower', 'position'.
        current_price: Current price (needed for Bollinger Bands assessment).
        volume_signal: Volume trend string (e.g. 'Bullish Accumulation').
        stochastic:    Stochastic dict with keys 'k', 'd', 'signal', 'zone'.

    Returns:
        Dict with keys: direction, raw_score, signals_used, votes.
    """
    bull_score = 0.0
    bear_score = 0.0
    signals_used: List[str] = []
    votes: Dict[str, str] = {}

    # RSI
    if rsi is not None:
        signals_used.append("rsi")
        if rsi <= 30:
            bull_score += _WEIGHTS["rsi"]
            votes["rsi"] = "Bullish (Oversold)"
        elif rsi >= 70:
            bear_score += _WEIGHTS["rsi"]
            votes["rsi"] = "Bearish (Overbought)"
        elif rsi < 45:
            bull_score += _WEIGHTS["rsi"] * 0.5
            votes["rsi"] = "Slight Bullish"
        elif rsi > 55:
            bear_score += _WEIGHTS["rsi"] * 0.5
            votes["rsi"] = "Slight Bearish"
        else:
            votes["rsi"] = "Neutral"

    # MACD
    if macd and isinstance(macd, dict):
        signals_used.append("macd")
        crossover = macd.get("crossover", "")
        macd_val = macd.get("macd", 0) or 0
        signal_val = macd.get("signal", 0) or 0
        if "Bullish" in str(crossover):
            bull_score += _WEIGHTS["macd"]
            votes["macd"] = "Bullish Crossover"
        elif "Bearish" in str(crossover):
            bear_score += _WEIGHTS["macd"]
            votes["macd"] = "Bearish Crossover"
        elif macd_val > signal_val:
            bull_score += _WEIGHTS["macd"] * 0.5
            votes["macd"] = "Slight Bullish (above signal)"
        elif macd_val < signal_val:
            bear_score += _WEIGHTS["macd"] * 0.5
            votes["macd"] = "Slight Bearish (below signal)"
        else:
            votes["macd"] = "Neutral"

    # Moving Average crossover
    if ma_signal:
        signals_used.append("ma")
        if "Golden" in ma_signal or "Bullish" in ma_signal:
            bull_score += _WEIGHTS["ma"]
            votes["ma"] = "Bullish (Golden Cross)"
        elif "Death" in ma_signal or "Bearish" in ma_signal:
            bear_score += _WEIGHTS["ma"]
            votes["ma"] = "Bearish (Death Cross)"
        else:
            votes["ma"] = "Neutral"

    # Bollinger Bands
    if bb and isinstance(bb, dict) and current_price is not None:
        signals_used.append("bb")
        position = bb.get("position", "")
        upper = bb.get("upper") or 0
        lower = bb.get("lower") or 0
        if current_price <= lower or position == "Oversold":
            bull_score += _WEIGHTS["bb"]
            votes["bb"] = "Bullish (Near Lower Band)"
        elif current_price >= upper or position == "Overbought":
            bear_score += _WEIGHTS["bb"]
            votes["bb"] = "Bearish (Near Upper Band)"
        else:
            votes["bb"] = "Neutral (Within Bands)"

    # Volume signal
    if volume_signal:
        signals_used.append("volume")
        if "Bullish" in volume_signal:
            bull_score += _WEIGHTS["volume"]
            votes["volume"] = "Bullish Accumulation"
        elif "Bearish" in volume_signal:
            bear_score += _WEIGHTS["volume"]
            votes["volume"] = "Bearish Distribution"
        else:
            votes["volume"] = "Neutral"

    # Stochastic
    if stochastic and isinstance(stochastic, dict):
        k = stochastic.get("k")
        if k is not None:
            signals_used.append("stoch")
            zone = stochastic.get("zone", "")
            sig = stochastic.get("signal", "")
            if zone == "Oversold" or sig == "Bullish":
                bull_score += _WEIGHTS["stoch"]
                votes["stoch"] = f"Bullish ({zone})"
            elif zone == "Overbought" or sig == "Bearish":
                bear_score += _WEIGHTS["stoch"]
                votes["stoch"] = f"Bearish ({zone})"
            else:
                votes["stoch"] = "Neutral"

    # Net score (positive = bullish, negative = bearish)
    raw_score = round(bull_score - bear_score, 4)

    if raw_score > 0.5:
        direction = "Bullish"
    elif raw_score < -0.5:
        direction = "Bearish"
    else:
        direction = "Neutral"

    return {
        "direction": direction,
        "raw_score": raw_score,
        "bull_score": round(bull_score, 4),
        "bear_score": round(bear_score, 4),
        "signals_used": signals_used,
        "votes": votes,
    }


# ── Strength & Confidence helpers ─────────────────────────────────────────────


def signal_strength_score(aggregated: Dict[str, Any]) -> float:
    """
    Convert an aggregated signal dict into a normalised strength score [0, 1].

    The score represents how "decisive" the signal is regardless of direction:
        1.0 = maximum conviction (all indicators agree on one side)
        0.0 = perfectly balanced / no signal

    Formula:
        raw_score is already in [-(sum of weights), +(sum of weights)].
        We normalise by the maximum possible absolute score (sum of all weights).

    Args:
        aggregated: Output of ``aggregate_signals()``.

    Returns:
        Float in [0, 1] representing signal strength.
    """
    raw = abs(aggregated.get("raw_score", 0.0))
    max_possible = sum(_WEIGHTS.values())
    if max_possible == 0:
        return 0.0
    return round(min(raw / max_possible, 1.0), 4)


def signal_confidence_label(strength: float) -> str:
    """
    Classify a normalised signal strength score into a textual confidence label.

    Thresholds:
        strength >= 0.75 → 'High Conviction'
        strength >= 0.45 → 'Moderate Conviction'
        strength >= 0.20 → 'Low Conviction'
        otherwise        → 'No Signal'

    Args:
        strength: Float in [0, 1] from ``signal_strength_score()``.

    Returns:
        One of: 'High Conviction', 'Moderate Conviction', 'Low Conviction', 'No Signal'.
    """
    if strength >= 0.75:
        return "High Conviction"
    if strength >= 0.45:
        return "Moderate Conviction"
    if strength >= 0.20:
        return "Low Conviction"
    return "No Signal"


# ── Markdown report ───────────────────────────────────────────────────────────


def format_trade_signals_report(
    ticker: str,
    aggregated: Dict[str, Any],
) -> str:
    """
    Render a Markdown trade signal summary for one ticker.

    Args:
        ticker:     Ticker symbol.
        aggregated: Output of ``aggregate_signals()``.

    Returns:
        Markdown-formatted string with direction, strength, confidence,
        and per-indicator vote breakdown.
    """
    direction = aggregated.get("direction", "N/A")
    raw_score = aggregated.get("raw_score", 0.0)
    votes = aggregated.get("votes", {})
    signals_used = aggregated.get("signals_used", [])

    strength = signal_strength_score(aggregated)
    confidence = signal_confidence_label(strength)

    dir_emoji = "🟢" if direction == "Bullish" else ("🔴" if direction == "Bearish" else "⚪")
    strength_bar = "█" * int(strength * 10) + "░" * (10 - int(strength * 10))

    lines = [
        f"### 📈 Trade Signals — {ticker}",
        "",
        f"**Direction:** {dir_emoji} {direction}  |  **Confidence:** {confidence}",
        f"**Strength:** [{strength_bar}] {strength:.0%}  "
        f"|  **Score:** {raw_score:+.2f}",
        "",
        f"**Indicators Used:** {len(signals_used)} / {len(_WEIGHTS)}",
        "",
        "| Indicator | Vote |",
        "|-----------|------|",
    ]

    indicator_labels = {
        "rsi": "RSI",
        "macd": "MACD",
        "ma": "MA Crossover",
        "bb": "Bollinger Bands",
        "volume": "Volume",
        "stoch": "Stochastic",
    }

    for key, label in indicator_labels.items():
        vote = votes.get(key, "—")
        vote_emoji = "🟢" if "Bullish" in vote else ("🔴" if "Bearish" in vote else "⚪")
        lines.append(f"| {label} | {vote_emoji} {vote} |")

    return "\n".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "aggregate_signals",
    "signal_strength_score",
    "signal_confidence_label",
    "format_trade_signals_report",
]

_MODULE = "tools/trade_signals"
_VERSION = "2.1.0"
