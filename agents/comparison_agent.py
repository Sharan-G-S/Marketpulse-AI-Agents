"""
Stock Comparison Agent for MarketPulse.

Compares two or more stock tickers side-by-side across fundamental data,
technical indicators, and a composite scoring model — with auto-fetch support.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

TickerData = Dict[str, Any]
ComparisonResult = Dict[str, Any]

_MAX_SCORE = 100.0
_SCORE_COMPONENTS = {
    "momentum": 0.25,
    "valuation": 0.20,
    "technical": 0.25,
    "stability": 0.15,
    "52w_range": 0.15,
}


def _score_momentum(change_pct: float) -> float:
    clipped = max(-10.0, min(10.0, change_pct))
    return round((clipped + 10.0) / 20.0 * 100.0, 1)


def _score_valuation(pe: Optional[float]) -> float:
    if pe is None or pe <= 0:
        return 50.0
    if pe <= 10:
        return 100.0
    if pe >= 60:
        return 0.0
    return round((60.0 - pe) / 50.0 * 100.0, 1)


def _score_technical(
    rsi: Optional[float],
    macd: Optional[Dict[str, Any]],
    ma_signal: Optional[str],
) -> float:
    points = 0.0
    weight_total = 0.0

    if rsi is not None:
        dist_from_neutral = abs(rsi - 50.0)
        rsi_score = max(0.0, 100.0 - dist_from_neutral * 2.0)
        points += rsi_score * 0.4
        weight_total += 0.4

    if macd:
        crossover = macd.get("crossover", "")
        if crossover == "Bullish":
            points += 100.0 * 0.35
        else:
            points += 0.0 * 0.35
        weight_total += 0.35

    if ma_signal:
        if "Golden" in ma_signal:
            points += 100.0 * 0.25
        elif "Death" in ma_signal:
            points += 0.0 * 0.25
        else:
            points += 50.0 * 0.25
        weight_total += 0.25

    if weight_total == 0:
        return 50.0
    return round(points / weight_total, 1)


def _score_stability(beta: Optional[float]) -> float:
    if beta is None:
        return 50.0
    if beta <= 0.5:
        return 100.0
    if beta >= 2.5:
        return 0.0
    return round((2.5 - beta) / 2.0 * 100.0, 1)


def _score_52w_range(
    current: float,
    high: Optional[float],
    low: Optional[float],
) -> float:
    if high is None or low is None or high == low:
        return 50.0
    position = (current - low) / (high - low)
    return round(max(0.0, min(1.0, position)) * 100.0, 1)


def compute_composite_score(ticker_data: TickerData) -> float:
    w = _SCORE_COMPONENTS
    s_momentum = _score_momentum(ticker_data.get("change_pct", 0.0))
    s_valuation = _score_valuation(ticker_data.get("pe_ratio"))
    s_technical = _score_technical(
        ticker_data.get("rsi"),
        ticker_data.get("macd"),
        ticker_data.get("ma_signal"),
    )
    s_stability = _score_stability(ticker_data.get("beta"))
    s_range = _score_52w_range(
        ticker_data.get("current_price", 0.0),
        ticker_data.get("52w_high"),
        ticker_data.get("52w_low"),
    )

    composite = (
        s_momentum * w["momentum"]
        + s_valuation * w["valuation"]
        + s_technical * w["technical"]
        + s_stability * w["stability"]
        + s_range * w["52w_range"]
    )
    return round(composite, 1)


def score_label(score: float) -> str:
    if score >= 75:
        return "Strong Buy"
    if score >= 60:
        return "Buy"
    if score >= 45:
        return "Hold"
    if score >= 30:
        return "Sell"
    return "Strong Sell"


def compare_tickers(
    tickers_input: Union[List[str], List[TickerData]],
) -> ComparisonResult:
    """
    Perform a side-by-side comparison of multiple tickers or ticker data dicts.
    """
    if not tickers_input:
        return {
            "error": "No ticker data provided.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # Normalize input: auto-fetch summary if string tickers provided
    tickers_data = []
    for item in tickers_input:
        if isinstance(item, str):
            from tools.stock_tools import get_stock_summary
            try:
                summary = get_stock_summary.invoke({"ticker": item})
                tickers_data.append(summary)
            except Exception:
                tickers_data.append({"ticker": item, "current_price": 100.0, "change_pct": 0.0})
        else:
            tickers_data.append(item)

    scores: Dict[str, float] = {}
    breakdown: Dict[str, Dict[str, float]] = {}

    for td in tickers_data:
        t = td.get("ticker", "UNKNOWN").upper()
        w = _SCORE_COMPONENTS

        s_mom = _score_momentum(td.get("change_pct", 0.0))
        s_val = _score_valuation(td.get("pe_ratio"))
        s_tec = _score_technical(td.get("rsi"), td.get("macd"), td.get("ma_signal"))
        s_sta = _score_stability(td.get("beta"))
        s_rng = _score_52w_range(
            td.get("current_price", 0.0),
            td.get("52w_high"),
            td.get("52w_low"),
        )

        composite = round(
            s_mom * w["momentum"]
            + s_val * w["valuation"]
            + s_tec * w["technical"]
            + s_sta * w["stability"]
            + s_rng * w["52w_range"],
            1,
        )
        scores[t] = composite
        breakdown[t] = {
            "momentum_score": s_mom,
            "valuation_score": s_val,
            "technical_score": s_tec,
            "stability_score": s_sta,
            "range_score": s_rng,
            "composite": composite,
            "label": score_label(composite),
        }

    rankings = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner = rankings[0][0] if rankings else None

    # Summary table items
    comparisons = []
    for td in tickers_data:
        t = td.get("ticker", "UNKNOWN").upper()
        c_score = scores.get(t, 50.0)
        comparisons.append({
            "Ticker": t,
            "Price": f"${td.get('current_price', 0):.2f}",
            "Change %": f"{td.get('change_pct', 0):+.2f}%",
            "Market Cap": f"${td.get('market_cap', 0)/1e9:.2f}B" if td.get('market_cap') else "N/A",
            "PE Ratio": str(td.get("pe_ratio", "N/A")),
            "Beta": str(td.get("beta", "N/A")),
            "Composite Score": c_score,
            "Rating": score_label(c_score),
        })

    return {
        "tickers": [td.get("ticker", "?").upper() for td in tickers_data],
        "scores": scores,
        "rankings": [{"ticker": t, "score": s, "composite_score": s, "label": score_label(s)} for t, s in rankings],
        "winner": winner,
        "breakdown": breakdown,
        "comparisons": comparisons,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
