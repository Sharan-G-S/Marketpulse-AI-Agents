"""
Price Alerts CLI — run threshold-based watchlist alerts from the terminal.

Usage:
    python tools/price_alerts_cli.py --tickers AAPL TSLA NVDA --pct 3.0
    python tools/price_alerts_cli.py --tickers AAPL --rsi-ob 75 --rsi-os 25
    python tools/price_alerts_cli.py --help
"""

import argparse
from datetime import datetime, timezone
import json
import sys
from typing import Any, Dict, List, Optional

from tools.watchlist_alerts import (
    DEFAULT_WATCHLIST_THRESHOLDS,
    evaluate_watchlist,
    watchlist_alert_summary,
)

# ── ANSI colour helpers (works on mac/linux) ──────────────────────────────────

_RED    = "\033[91m"
_YELLOW = "\033[93m"
_BLUE   = "\033[94m"
_GREEN  = "\033[92m"
_BOLD   = "\033[1m"
_RESET  = "\033[0m"


def _colour(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


def _severity_colour(severity: str) -> str:
    return {
        "CRITICAL": _RED,
        "WARNING":  _YELLOW,
        "INFO":     _BLUE,
    }.get(severity, _RESET)


# ── Output formatters ─────────────────────────────────────────────────────────

def print_alerts(alerts: List[Dict[str, Any]], *, use_colour: bool = True) -> None:
    """Print a list of alert dicts to stdout with optional ANSI colouring."""
    if not alerts:
        msg = _colour("✅  No alerts triggered.", _GREEN) if use_colour else "No alerts triggered."
        print(msg)
        return

    for a in alerts:
        sev   = a["severity"]
        col   = _severity_colour(sev) if use_colour else ""
        reset = _RESET if use_colour else ""
        print(
            f"{col}[{sev}]{reset}  "
            f"{_colour(a['ticker'], _BOLD) if use_colour else a['ticker']}  "
            f"{a['message']}  "
            f"(value={a['value']:.2f}, threshold={a['threshold']:.2f})"
        )


def print_summary(summary: Dict[str, Any], *, use_colour: bool = True) -> None:
    """Print the summary status line."""
    status = summary.get("status", "")
    total  = summary.get("total", 0)
    counts = summary.get("counts", {})
    print()
    print(_colour(status, _BOLD) if use_colour else status)
    print(
        f"  Total: {total}  |  "
        f"Critical: {counts.get('CRITICAL', 0)}  |  "
        f"Warning: {counts.get('WARNING', 0)}  |  "
        f"Info: {counts.get('INFO', 0)}"
    )
    print()


def output_json(alerts: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    """Dump alerts + summary as JSON to stdout."""
    print(json.dumps({"summary": summary, "alerts": alerts}, indent=2))


# ── Mock data builder (used when no live fetch is available) ──────────────────

def _build_mock_entry(ticker: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Return a mock WatchlistEntry for a ticker using provided overrides."""
    return {
        "ticker":        ticker.upper(),
        "current_price": overrides.get("price", 150.0),
        "change_pct":    overrides.get("change_pct", 0.0),
        "volume":        overrides.get("volume"),
        "avg_volume":    overrides.get("avg_volume"),
        "rsi":           overrides.get("rsi"),
    }


# ── Live fetch (best-effort, fails gracefully) ────────────────────────────────

def _fetch_entry(ticker: str) -> Dict[str, Any]:
    """Fetch live market data for a ticker. Falls back to mock on error."""
    try:
        from tools.indicators import get_all_indicators
        from tools.stock_tools import get_price_history, get_stock_summary

        summary = get_stock_summary.invoke({"ticker": ticker})
        history = get_price_history.invoke({"ticker": ticker, "period": "5d", "interval": "1d"})
        inds    = get_all_indicators(history)

        return {
            "ticker":        ticker.upper(),
            "current_price": summary.get("current_price", 0.0),
            "change_pct":    summary.get("change_pct", 0.0),
            "volume":        summary.get("volume"),
            "avg_volume":    summary.get("averageVolume") or summary.get("avg_volume"),
            "rsi":           inds.get("rsi"),
        }
    except Exception:
        return _build_mock_entry(ticker, {})


# ── CLI entry point ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="price_alerts_cli",
        description="MarketPulse — run watchlist price / RSI / volume alerts from the CLI.",
    )
    p.add_argument("--tickers",  nargs="+", required=True, metavar="TICKER",
                   help="One or more ticker symbols (e.g. AAPL TSLA NVDA)")
    p.add_argument("--pct",      type=float, default=DEFAULT_WATCHLIST_THRESHOLDS["price_change_pct"],
                   metavar="PCT", help="Price move %% alert threshold (default %(default)s)")
    p.add_argument("--rsi-ob",   type=float, default=DEFAULT_WATCHLIST_THRESHOLDS["rsi_overbought"],
                   metavar="RSI", help="RSI overbought level (default %(default)s)")
    p.add_argument("--rsi-os",   type=float, default=DEFAULT_WATCHLIST_THRESHOLDS["rsi_oversold"],
                   metavar="RSI", help="RSI oversold level (default %(default)s)")
    p.add_argument("--vol-spike", type=float, default=DEFAULT_WATCHLIST_THRESHOLDS["volume_spike"],
                   metavar="X",   help="Volume spike multiplier (default %(default)s)")
    p.add_argument("--json",     action="store_true",
                   help="Output raw JSON instead of human-readable text")
    p.add_argument("--no-colour", action="store_true",
                   help="Disable ANSI colour output")
    p.add_argument("--mock",     action="store_true",
                   help="Skip live fetch; use zero-change mock data (for testing)")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args   = parser.parse_args(argv)

    tickers = [t.upper() for t in args.tickers]
    thresholds = {
        "price_change_pct": args.pct,
        "rsi_overbought":   args.rsi_ob,
        "rsi_oversold":     args.rsi_os,
        "volume_spike":     args.vol_spike,
    }

    use_colour = not args.no_colour and sys.stdout.isatty()

    if not args.json:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        print(_colour(f"\n📡 MarketPulse Price Alert Scanner — {ts}", _BOLD) if use_colour
              else f"\nMarketPulse Price Alert Scanner — {ts}")
        print(f"Tickers: {', '.join(tickers)}\n")

    entries = []
    for t in tickers:
        entry = _build_mock_entry(t, {}) if args.mock else _fetch_entry(t)
        entries.append(entry)

    alerts  = evaluate_watchlist(entries, thresholds)
    summary = watchlist_alert_summary(alerts)

    if args.json:
        output_json(alerts, summary)
    else:
        print_alerts(alerts, use_colour=use_colour)
        print_summary(summary, use_colour=use_colour)

    return 1 if summary.get("counts", {}).get("CRITICAL", 0) else 0


if __name__ == "__main__":
    sys.exit(main())

_MODULE = "tools/price_alerts_cli.py"
_VERSION = "1.7.0"
