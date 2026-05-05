"""
Price History Export Utility for MarketPulse.

Exports OHLCV (Open/High/Low/Close/Volume) price history to CSV or JSON
with configurable period, interval, and optional technical enrichment.

No LLM required — pure data serialisation.
"""

import csv
from datetime import datetime, timezone
import io
import json
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------

OHLCV_COLUMNS = ["date", "open", "high", "low", "close", "volume"]

ENRICHED_COLUMNS = OHLCV_COLUMNS + [
    "daily_change",      # close - previous close
    "daily_change_pct",  # % change from previous close
    "typical_price",     # (H + L + C) / 3
    "range",             # high - low
]


# ---------------------------------------------------------------------------
# Enrichment helpers
# ---------------------------------------------------------------------------

def enrich_ohlcv(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add derived columns to a list of OHLCV records.

    Adds:
        - daily_change      : close − previous_close
        - daily_change_pct  : (close − prev_close) / prev_close × 100
        - typical_price     : (high + low + close) / 3
        - range             : high − low

    Args:
        records: List of OHLCV dicts (oldest first).

    Returns:
        New list with enriched dicts; first record has None for change fields.
    """
    enriched = []
    prev_close: Optional[float] = None

    for row in records:
        h = row.get("high") or 0.0
        l = row.get("low") or 0.0
        c = row.get("close") or 0.0

        daily_change = round(c - prev_close, 4) if prev_close is not None else None
        daily_change_pct = (
            round((c - prev_close) / prev_close * 100, 2)
            if prev_close and prev_close != 0
            else None
        )
        typical_price = round((h + l + c) / 3, 4) if (h or l or c) else None
        price_range = round(h - l, 4) if (h is not None and l is not None) else None

        enriched.append({
            **row,
            "daily_change":     daily_change,
            "daily_change_pct": daily_change_pct,
            "typical_price":    typical_price,
            "range":            price_range,
        })
        prev_close = c if c else prev_close

    return enriched


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def export_price_history_csv(
    records: List[Dict[str, Any]],
    ticker: str,
    enrich: bool = True,
) -> str:
    """
    Serialise OHLCV price history to a UTF-8 CSV string.

    Args:
        records: List of OHLCV dicts from get_price_history tool.
        ticker:  Ticker symbol (added as first column).
        enrich:  Whether to compute and include derived columns.

    Returns:
        CSV string with header row.
    """
    if not records:
        return ""

    rows = enrich_ohlcv(records) if enrich else records
    columns = (["ticker"] + ENRICHED_COLUMNS) if enrich else (["ticker"] + OHLCV_COLUMNS)

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=columns,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()

    for row in rows:
        cleaned = {k: ("" if v is None else v) for k, v in row.items()}
        cleaned["ticker"] = ticker.upper()
        writer.writerow(cleaned)

    return buffer.getvalue()


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def export_price_history_json(
    records: List[Dict[str, Any]],
    ticker: str,
    enrich: bool = True,
) -> str:
    """
    Serialise OHLCV price history to a formatted JSON string.

    Returns a JSON object with metadata and a ``data`` array:
    {
        "ticker":        "AAPL",
        "record_count":  N,
        "exported_at":   "ISO-8601",
        "data":          [ {ohlcv row}, ... ]
    }
    """
    if not records:
        return json.dumps({"ticker": ticker, "record_count": 0, "data": []})

    rows = enrich_ohlcv(records) if enrich else records

    payload = {
        "ticker":       ticker.upper(),
        "record_count": len(rows),
        "exported_at":  datetime.now(timezone.utc).isoformat(),
        "enriched":     enrich,
        "data":         rows,
    }
    return json.dumps(payload, indent=2, default=str)


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def price_history_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute summary statistics from an OHLCV record list.

    Returns:
        Dict with period_high, period_low, avg_close, avg_volume,
        total_days, best_day (date, pct), worst_day (date, pct).
    """
    if not records:
        return {}

    closes  = [r["close"]  for r in records if r.get("close")  is not None]
    highs   = [r["high"]   for r in records if r.get("high")   is not None]
    lows    = [r["low"]    for r in records if r.get("low")    is not None]
    volumes = [r["volume"] for r in records if r.get("volume") is not None]

    enriched = enrich_ohlcv(records)
    daily_changes = [
        (r["date"], r["daily_change_pct"])
        for r in enriched
        if r.get("daily_change_pct") is not None
    ]

    best  = max(daily_changes, key=lambda x: x[1])  if daily_changes else (None, None)
    worst = min(daily_changes, key=lambda x: x[1])  if daily_changes else (None, None)

    return {
        "period_high":  round(max(highs),  2) if highs  else None,
        "period_low":   round(min(lows),   2) if lows   else None,
        "avg_close":    round(sum(closes)  / len(closes),  2) if closes  else None,
        "avg_volume":   round(sum(volumes) / len(volumes))    if volumes else None,
        "total_days":   len(records),
        "best_day":     {"date": best[0],  "change_pct": best[1]}  if best[0]  else None,
        "worst_day":    {"date": worst[0], "change_pct": worst[1]} if worst[0] else None,
    }
