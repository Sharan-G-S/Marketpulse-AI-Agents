"""
Market Calendar — upcoming earnings dates and key market events.

Provides deterministic, data-driven helpers for:
  - Estimating next earnings date from a yfinance summary
  - Generating a week-ahead market events calendar
  - Formatting events as Markdown tables

No LLM required — uses yfinance metadata and standard calendar arithmetic.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# ── Type aliases ──────────────────────────────────────────────────────────────

MarketEvent = Dict[str, Any]
"""
{
    "date":        str,        # YYYY-MM-DD
    "event_type":  str,        # "earnings" | "ex_dividend" | "holiday" | "note"
    "ticker":      str | None,
    "description": str,
    "importance":  "high" | "medium" | "low",
}
"""

# ── US Market Holiday list (fixed dates, approximate) ─────────────────────────

US_MARKET_HOLIDAYS_2026: List[str] = [
    "2026-01-01",  # New Year's Day
    "2026-01-19",  # MLK Day
    "2026-02-16",  # Presidents' Day
    "2026-04-03",  # Good Friday
    "2026-05-25",  # Memorial Day
    "2026-07-03",  # Independence Day (observed)
    "2026-09-07",  # Labor Day
    "2026-11-26",  # Thanksgiving
    "2026-11-27",  # Day after Thanksgiving (early close)
    "2026-12-25",  # Christmas
]


# ── Earnings date estimation ──────────────────────────────────────────────────

def extract_earnings_date(stock_summary: Dict[str, Any]) -> Optional[str]:
    """
    Extract the next earnings date from a yfinance stock summary dict.

    Checks common field names returned by yfinance calendar data:
    earningsDate, nextEarningsDate, earningsTimestamp.

    Args:
        stock_summary: Dict from get_stock_summary or yfinance.Ticker.info.

    Returns:
        ISO date string YYYY-MM-DD or None if not available.
    """
    for key in ("earningsDate", "nextEarningsDate", "earnings_date"):
        raw = stock_summary.get(key)
        if raw:
            if isinstance(raw, (list, tuple)):
                raw = raw[0]
            try:
                if isinstance(raw, (int, float)):
                    return datetime.fromtimestamp(int(raw), tz=timezone.utc).strftime("%Y-%m-%d")
                return str(raw)[:10]
            except Exception:
                continue

    # fallback: use earningsTimestamp
    ts = stock_summary.get("earningsTimestamp")
    if ts:
        try:
            return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            pass

    return None


def extract_ex_dividend_date(stock_summary: Dict[str, Any]) -> Optional[str]:
    """Extract the ex-dividend date from a stock summary dict."""
    for key in ("exDividendDate", "ex_dividend_date"):
        raw = stock_summary.get(key)
        if raw:
            try:
                if isinstance(raw, (int, float)):
                    return datetime.fromtimestamp(int(raw), tz=timezone.utc).strftime("%Y-%m-%d")
                return str(raw)[:10]
            except Exception:
                continue
    return None


# ── Event list builders ───────────────────────────────────────────────────────

def build_ticker_events(
    ticker: str,
    stock_summary: Dict[str, Any],
) -> List[MarketEvent]:
    """
    Build a list of upcoming market events for a single ticker.

    Args:
        ticker:        Stock symbol (uppercase).
        stock_summary: yfinance-style info dict for the ticker.

    Returns:
        List of MarketEvent dicts, sorted by date.
    """
    events: List[MarketEvent] = []
    today = date.today()

    earnings_date = extract_earnings_date(stock_summary)
    if earnings_date:
        try:
            ed = date.fromisoformat(earnings_date)
            if ed >= today:
                events.append({
                    "date":        earnings_date,
                    "event_type":  "earnings",
                    "ticker":      ticker.upper(),
                    "description": f"{ticker.upper()} Q earnings report",
                    "importance":  "high",
                })
        except ValueError:
            pass

    ex_div = extract_ex_dividend_date(stock_summary)
    if ex_div:
        try:
            dd = date.fromisoformat(ex_div)
            if dd >= today:
                events.append({
                    "date":        ex_div,
                    "event_type":  "ex_dividend",
                    "ticker":      ticker.upper(),
                    "description": f"{ticker.upper()} ex-dividend date",
                    "importance":  "medium",
                })
        except ValueError:
            pass

    return sorted(events, key=lambda e: e["date"])


def build_market_calendar(
    ticker_summaries: Dict[str, Dict[str, Any]],
    include_holidays: bool = True,
    days_ahead: int = 30,
) -> List[MarketEvent]:
    """
    Build a combined market calendar from multiple ticker summaries.

    Args:
        ticker_summaries: Dict mapping ticker → stock_summary dict.
        include_holidays: Whether to include US market holidays.
        days_ahead:       Only include events within this many days.

    Returns:
        Sorted list of MarketEvent dicts.
    """
    events: List[MarketEvent] = []
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    # Per-ticker events
    for ticker, summary in ticker_summaries.items():
        for e in build_ticker_events(ticker, summary):
            try:
                if date.fromisoformat(e["date"]) <= cutoff:
                    events.append(e)
            except ValueError:
                pass

    # US market holidays
    if include_holidays:
        for h in US_MARKET_HOLIDAYS_2026:
            try:
                hd = date.fromisoformat(h)
                if today <= hd <= cutoff:
                    events.append({
                        "date":        h,
                        "event_type":  "holiday",
                        "ticker":      None,
                        "description": "US Market Holiday",
                        "importance":  "low",
                    })
            except ValueError:
                pass

    return sorted(events, key=lambda e: e["date"])


# ── Formatting ────────────────────────────────────────────────────────────────

_EVENT_EMOJI = {
    "earnings":    "📊",
    "ex_dividend": "💰",
    "holiday":     "🏖️",
    "note":        "📌",
}

_IMPORTANCE_BADGE = {
    "high":   "🔴 High",
    "medium": "🟡 Medium",
    "low":    "🟢 Low",
}


def format_calendar_markdown(events: List[MarketEvent]) -> str:
    """
    Render a market event calendar as a Markdown table.

    Args:
        events: Sorted list of MarketEvent dicts.

    Returns:
        Markdown string with a table and event count header.
    """
    if not events:
        return "_No upcoming market events found for the selected period._"

    lines = [
        f"### 📅 Market Calendar ({len(events)} event(s))\n",
        "| Date | Event | Ticker | Importance |",
        "|------|-------|--------|------------|",
    ]

    for e in events:
        emoji = _EVENT_EMOJI.get(e["event_type"], "📌")
        badge = _IMPORTANCE_BADGE.get(e["importance"], e["importance"])
        ticker_col = e["ticker"] or "—"
        lines.append(f"| {e['date']} | {emoji} {e['description']} | {ticker_col} | {badge} |")

    return "\n".join(lines)


def upcoming_earnings_list(
    ticker_summaries: Dict[str, Dict[str, Any]],
    days_ahead: int = 30,
) -> List[Dict[str, str]]:
    """
    Return a simple list of dicts with ticker + earnings date for tickers
    that have an upcoming earnings date within *days_ahead* days.
    """
    today  = date.today()
    cutoff = today + timedelta(days=days_ahead)
    result = []
    for ticker, summary in ticker_summaries.items():
        ed = extract_earnings_date(summary)
        if ed:
            try:
                if today <= date.fromisoformat(ed) <= cutoff:
                    result.append({"ticker": ticker.upper(), "earnings_date": ed})
            except ValueError:
                pass
    return sorted(result, key=lambda x: x["earnings_date"])
