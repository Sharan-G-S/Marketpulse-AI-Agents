"""
Portfolio Correlation Analysis for MarketPulse.

Computes pairwise Pearson correlation between tickers from daily returns,
and rolling correlation for dynamic relationship tracking.

No LLM required — pure statistics.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

# ── Internal helpers ──────────────────────────────────────────────────────────


def _daily_returns(closes: List[float]) -> List[float]:
    """Compute daily percentage returns from a list of closing prices."""
    if len(closes) < 2:
        return []
    return [
        (closes[i] - closes[i - 1]) / closes[i - 1] if closes[i - 1] != 0.0 else 0.0
        for i in range(1, len(closes))
    ]


def _pearson(x: List[float], y: List[float]) -> Optional[float]:
    """
    Compute Pearson correlation coefficient between two equal-length series.

    Returns None if the series have insufficient length or zero standard deviation.
    """
    n = len(x)
    if n < 2 or len(y) != n:
        return None

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denom_x = math.sqrt(sum((v - mean_x) ** 2 for v in x))
    denom_y = math.sqrt(sum((v - mean_y) ** 2 for v in y))

    if denom_x == 0.0 or denom_y == 0.0:
        return None

    return round(num / (denom_x * denom_y), 4)


# ── Core public functions ─────────────────────────────────────────────────────

def compute_correlation_matrix(
    price_histories: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Compute a pairwise Pearson correlation matrix for a set of tickers.

    Args:
        price_histories: Dict mapping ticker symbol → OHLCV record list
                         (sorted oldest-first, each record must have a 'close' key).

    Returns:
        Nested dict: matrix[ticker_a][ticker_b] = correlation coefficient or None.
    """
    tickers = list(price_histories.keys())
    returns: Dict[str, List[float]] = {}

    for ticker, history in price_histories.items():
        closes = [r["close"] for r in history if r.get("close") is not None]
        returns[ticker] = _daily_returns(closes)

    matrix: Dict[str, Dict[str, Optional[float]]] = {}
    for a in tickers:
        matrix[a] = {}
        for b in tickers:
            if a == b:
                matrix[a][b] = 1.0
            else:
                ra, rb = returns[a], returns[b]
                min_len = min(len(ra), len(rb))
                if min_len < 2:
                    matrix[a][b] = None
                else:
                    matrix[a][b] = _pearson(ra[-min_len:], rb[-min_len:])

    return matrix


def compute_rolling_correlation(
    history_a: List[Dict[str, Any]],
    history_b: List[Dict[str, Any]],
    window: int = 20,
) -> List[Tuple[int, Optional[float]]]:
    """
    Compute rolling Pearson correlation between two tickers over a sliding window.

    Args:
        history_a: OHLCV list for ticker A (oldest first).
        history_b: OHLCV list for ticker B (oldest first).
        window: Number of bars for each rolling window (default 20).

    Returns:
        List of (bar_index, correlation) tuples.  Correlation is None for the
        initial window warm-up period.
    """
    closes_a = [r["close"] for r in history_a if r.get("close") is not None]
    closes_b = [r["close"] for r in history_b if r.get("close") is not None]

    min_len = min(len(closes_a), len(closes_b))
    if min_len < 2:
        return []

    ra = _daily_returns(closes_a[:min_len])
    rb = _daily_returns(closes_b[:min_len])
    n = len(ra)

    result: List[Tuple[int, Optional[float]]] = []
    for i in range(n):
        if i + 1 < window:
            result.append((i, None))
        else:
            slice_a = ra[i + 1 - window: i + 1]
            slice_b = rb[i + 1 - window: i + 1]
            result.append((i, _pearson(slice_a, slice_b)))

    return result


# ── Display helpers ───────────────────────────────────────────────────────────


def correlation_label(corr: Optional[float]) -> str:
    """
    Classify a Pearson correlation coefficient into a human-readable label.

    Returns one of: 'Strong Positive', 'Moderate Positive',
    'Weak / No Correlation', 'Moderate Negative', 'Strong Negative', or 'N/A'.
    """
    if corr is None:
        return "N/A"
    if corr >= 0.7:
        return "Strong Positive"
    if corr >= 0.4:
        return "Moderate Positive"
    if corr > -0.4:
        return "Weak / No Correlation"
    if corr > -0.7:
        return "Moderate Negative"
    return "Strong Negative"


def format_correlation_report(
    matrix: Dict[str, Dict[str, Optional[float]]],
    title: str = "Correlation Matrix",
) -> str:
    """
    Render a pairwise correlation matrix as a Markdown table.

    Args:
        matrix: Output of ``compute_correlation_matrix()``.
        title:  Report heading.

    Returns:
        Markdown-formatted string with the correlation table.
    """
    tickers = list(matrix.keys())
    if not tickers:
        return "_No correlation data available._"

    header = "| Ticker | " + " | ".join(tickers) + " |"
    sep = "|--------|" + "---------|" * len(tickers)
    rows = [header, sep]

    for a in tickers:
        cells = []
        for b in tickers:
            val = matrix[a].get(b)
            if val is None:
                cells.append("N/A")
            elif a == b:
                cells.append("1.00")
            else:
                emoji = "🟢" if val >= 0.4 else ("🔴" if val <= -0.4 else "⚪")
                cells.append(f"{emoji} {val:.2f}")
        rows.append("| " + a + " | " + " | ".join(cells) + " |")

    return f"### 📊 {title}\n\n" + "\n".join(rows)


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "compute_correlation_matrix",
    "compute_rolling_correlation",
    "correlation_label",
    "format_correlation_report",
]

_MODULE = "tools/correlation"
_VERSION = "2.1.0"
