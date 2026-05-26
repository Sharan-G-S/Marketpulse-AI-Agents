"""
Data Quality Validator for MarketPulse.

Validates raw price history and stock summary dicts for completeness,
plausibility, and consistency before they are passed to downstream
analytics engines. Returns structured validation reports.

No LLM — pure rule-based checks.
"""

from typing import Any, Dict, List, Optional, Tuple

# ── Validation result types ───────────────────────────────────────────────────

Issue = Dict[str, str]
"""
{
    "field":    str,   # field name or "global"
    "level":    str,   # "error" | "warning" | "info"
    "message":  str,
}
"""

ValidationReport = Dict[str, Any]
"""
{
    "valid":   bool,
    "score":   float,   # 0-100 quality score
    "issues":  List[Issue],
    "errors":  int,
    "warnings":int,
}
"""


# ── Issue builders ────────────────────────────────────────────────────────────

def _error(field: str, message: str) -> Issue:
    return {"field": field, "level": "error", "message": message}


def _warning(field: str, message: str) -> Issue:
    return {"field": field, "level": "warning", "message": message}


def _info(field: str, message: str) -> Issue:
    return {"field": field, "level": "info", "message": message}


# ── Price history validation ──────────────────────────────────────────────────

_PRICE_FIELDS = ("open", "high", "low", "close", "volume")


def validate_bar(bar: Dict[str, Any], index: int) -> List[Issue]:
    """Validate a single OHLCV bar dict."""
    issues: List[Issue] = []
    prefix = f"bar[{index}]"

    for field in ("open", "high", "low", "close"):
        val = bar.get(field)
        if val is None:
            issues.append(_error(f"{prefix}.{field}", f"Missing required field '{field}'."))
            continue
        try:
            fval = float(val)
            if fval <= 0:
                issues.append(_warning(f"{prefix}.{field}", f"'{field}' is non-positive ({fval})."))
        except (ValueError, TypeError):
            issues.append(_error(f"{prefix}.{field}", f"'{field}' is not numeric (got {val!r})."))

    # OHLC consistency — only check close/open range when high >= low is sane
    try:
        o = float(bar.get("open",  0))
        h = float(bar.get("high",  0))
        l = float(bar.get("low",   0))
        c = float(bar.get("close", 0))
        if h < l:
            issues.append(_error(prefix, f"High ({h}) < Low ({l}) — impossible OHLC."))
        else:
            # These checks are only meaningful when the H/L range is valid
            if c > h or c < l:
                issues.append(_warning(prefix, f"Close ({c}) outside High-Low range [{l}, {h}]."))
            if o > h or o < l:
                issues.append(_warning(prefix, f"Open ({o}) outside High-Low range [{l}, {h}]."))
    except (ValueError, TypeError):
        pass  # numeric errors already flagged above

    # Volume sanity (warning only — some tickers have legitimate zero-volume bars)
    vol = bar.get("volume")
    if vol is not None:
        try:
            if float(vol) < 0:
                issues.append(_warning(f"{prefix}.volume", f"Volume is negative ({vol})."))
        except (ValueError, TypeError):
            issues.append(_warning(f"{prefix}.volume", "Volume is not numeric."))

    return issues


def validate_price_history(
    history: List[Dict[str, Any]],
    min_bars: int = 5,
) -> ValidationReport:
    """
    Validate a list of OHLCV bars.

    Args:
        history:  List of bar dicts.
        min_bars: Minimum number of bars required (default 5).

    Returns:
        ValidationReport dict.
    """
    issues: List[Issue] = []

    if not history:
        return {
            "valid":    False,
            "score":    0.0,
            "issues":   [_error("global", "Price history is empty.")],
            "errors":   1,
            "warnings": 0,
        }

    if len(history) < min_bars:
        issues.append(_warning(
            "global",
            f"Only {len(history)} bars — fewer than minimum {min_bars}. Results may be unreliable.",
        ))

    for i, bar in enumerate(history):
        issues.extend(validate_bar(bar, i))

    # Check for duplicate dates
    dates = [bar.get("date") or bar.get("Date") for bar in history]
    non_null = [d for d in dates if d is not None]
    if len(non_null) != len(set(non_null)):
        issues.append(_warning("global", "Duplicate date entries detected in price history."))

    errors   = sum(1 for i in issues if i["level"] == "error")
    warnings = sum(1 for i in issues if i["level"] == "warning")
    # Score: deduct points per issue; cap at 0. Penalty is absolute, not ratio-based.
    penalty = errors * 15 + warnings * 5
    score = max(0.0, round(100.0 - penalty, 2))

    return {
        "valid":    errors == 0,
        "score":    score,
        "issues":   issues,
        "errors":   errors,
        "warnings": warnings,
    }


# ── Stock summary validation ──────────────────────────────────────────────────

_SUMMARY_REQUIRED = ("ticker", "current_price")
_SUMMARY_OPTIONAL = ("change_pct", "volume", "market_cap", "pe_ratio", "52w_high", "52w_low")


def validate_stock_summary(summary: Dict[str, Any]) -> ValidationReport:
    """
    Validate a stock summary dict from get_stock_summary.

    Args:
        summary: Dict with stock metadata and current price.

    Returns:
        ValidationReport dict.
    """
    issues: List[Issue] = []

    for field in _SUMMARY_REQUIRED:
        if summary.get(field) is None:
            issues.append(_error(field, f"Required field '{field}' is missing."))

    price = summary.get("current_price")
    if price is not None:
        try:
            if float(price) <= 0:
                issues.append(_warning("current_price", f"Price is non-positive ({price})."))
        except (ValueError, TypeError):
            issues.append(_error("current_price", f"Price is not numeric ({price!r})."))

    change_pct = summary.get("change_pct")
    if change_pct is not None:
        try:
            pct = float(change_pct)
            if abs(pct) > 50:
                issues.append(_warning(
                    "change_pct",
                    f"change_pct of {pct:.1f}% is unusually large — verify data source.",
                ))
        except (ValueError, TypeError):
            issues.append(_warning("change_pct", "change_pct is not numeric."))

    missing_optional = [f for f in _SUMMARY_OPTIONAL if summary.get(f) is None]
    if missing_optional:
        issues.append(_info(
            "optional_fields",
            f"Optional fields missing: {', '.join(missing_optional)}.",
        ))

    errors   = sum(1 for i in issues if i["level"] == "error")
    warnings = sum(1 for i in issues if i["level"] == "warning")
    score = max(0.0, round(100.0 - errors * 20 - warnings * 5, 2))

    return {
        "valid":    errors == 0,
        "score":    score,
        "issues":   issues,
        "errors":   errors,
        "warnings": warnings,
    }


# ── Combined report formatter ─────────────────────────────────────────────────

def format_validation_report(report: ValidationReport, label: str = "Data") -> str:
    """Render a ValidationReport as a Markdown summary."""
    status = "✅ Valid" if report["valid"] else "❌ Invalid"
    lines = [
        f"### 🔍 Data Quality Report — {label}",
        f"**Status:** {status}  |  **Score:** {report['score']:.1f}/100  |  "
        f"**Errors:** {report['errors']}  |  **Warnings:** {report['warnings']}",
        "",
    ]
    issues = report.get("issues", [])
    if not issues:
        lines.append("_No issues detected._")
    else:
        icons = {"error": "🔴", "warning": "🟡", "info": "🔵"}
        for iss in issues:
            icon = icons.get(iss["level"], "⚪")
            lines.append(f"- {icon} **{iss['level'].upper()}** `{iss['field']}`: {iss['message']}")
    return "\n".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = [
    "validate_bar",
    "validate_price_history",
    "validate_stock_summary",
    "format_validation_report",
]

_MODULE = "tools.data_quality"
_VERSION = "1.7.8"
