"""
CSV Export Utility for MarketPulse.

Provides functions to serialise portfolio positions, watchlist entries,
and triggered alerts to CSV format — both as in-memory strings (for
Streamlit download buttons) and as files on disk.
"""

import csv
import io
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------

PORTFOLIO_COLUMNS = [
    "ticker",
    "quantity",
    "avg_price",
    "current_price",
    "cost_basis",
    "market_value",
    "unrealised_pnl",
    "pnl_pct",
    "sector",
    "beta",
]

WATCHLIST_COLUMNS = [
    "ticker",
    "price",
    "change_pct",
    "trend",
    "market_cap",
    "pe_ratio",
    "sector",
    "rsi",
    "rsi_signal",
]

ALERT_COLUMNS = [
    "ticker",
    "type",
    "severity",
    "message",
    "current_value",
    "triggered_at",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _rows_to_csv_string(rows: List[Dict[str, Any]], columns: List[str]) -> str:
    """
    Convert a list of dicts to a CSV string using the given column order.

    Columns missing from a row are written as empty strings.

    Args:
        rows:    List of dicts representing data rows.
        columns: Ordered list of column names / dict keys.

    Returns:
        UTF-8 CSV string with header row.
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=columns,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        # Replace None with empty string for clean CSV output
        cleaned = {k: ("" if v is None else v) for k, v in row.items()}
        writer.writerow(cleaned)
    return buffer.getvalue()


def _timestamped_filename(prefix: str) -> str:
    """Generate a filename like 'marketpulse_portfolio_20250503_143000.csv'."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"marketpulse_{prefix}_{ts}.csv"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def export_portfolio_csv(
    positions: List[Dict[str, Any]],
) -> str:
    """
    Convert enriched portfolio positions to a CSV string.

    Args:
        positions: List of enriched position dicts from ``analyse_portfolio``.

    Returns:
        UTF-8 CSV string ready for download or file write.
    """
    return _rows_to_csv_string(positions, PORTFOLIO_COLUMNS)


def export_watchlist_csv(
    watchlist: List[Dict[str, Any]],
) -> str:
    """
    Convert watchlist entries to a CSV string.

    Args:
        watchlist: List of ticker dicts from ``watchlist_agent``.

    Returns:
        UTF-8 CSV string ready for download or file write.
    """
    return _rows_to_csv_string(watchlist, WATCHLIST_COLUMNS)


def export_alerts_csv(
    alerts: List[Dict[str, Any]],
) -> str:
    """
    Convert triggered alert records to a CSV string.

    Args:
        alerts: List of alert dicts stored in state by the watchlist agent.

    Returns:
        UTF-8 CSV string ready for download or file write.
    """
    return _rows_to_csv_string(alerts, ALERT_COLUMNS)


def save_csv_to_disk(
    csv_content: str,
    prefix: str,
    output_dir: str = "./reports",
) -> str:
    """
    Write a CSV string to disk and return the file path.

    Args:
        csv_content: CSV string to write.
        prefix:      Filename prefix, e.g. 'portfolio', 'watchlist'.
        output_dir:  Directory to write to (created if needed).

    Returns:
        Absolute path of the written file.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = _timestamped_filename(prefix)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        fh.write(csv_content)
    return os.path.abspath(filepath)


def export_summary_csv(
    portfolio_result: Optional[Dict[str, Any]] = None,
    watchlist: Optional[List[Dict[str, Any]]] = None,
    alerts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, str]:
    """
    Convenience function — export all available datasets to CSV strings.

    Returns:
        Dict with keys 'portfolio', 'watchlist', 'alerts' mapped to
        their respective CSV strings (or empty string if data not provided).
    """
    result: Dict[str, str] = {
        "portfolio": "",
        "watchlist": "",
        "alerts": "",
    }

    if portfolio_result:
        positions = portfolio_result.get("positions", [])
        if positions:
            result["portfolio"] = export_portfolio_csv(positions)

    if watchlist:
        result["watchlist"] = export_watchlist_csv(watchlist)

    if alerts:
        result["alerts"] = export_alerts_csv(alerts)

    return result
