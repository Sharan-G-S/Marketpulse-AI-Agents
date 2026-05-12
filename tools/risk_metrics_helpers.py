"""
Risk Metrics Formatting Helpers for MarketPulse.

Renders compute_risk_metrics() output as Markdown tables,
colour-coded labels, and plain dicts for Streamlit DataFrames.
"""

from typing import Any, Dict, List

# ── Colour helpers ──────────────────────────────────────────────────────────

def risk_label_emoji(label: str) -> str:
    return {
        "Low":       "🟢 Low",
        "Moderate":  "🟡 Moderate",
        "High":      "🔴 High",
        "Very High": "💥 Very High",
    }.get(label, label)


def sharpe_badge(sharpe: float) -> str:
    if sharpe >= 2.0:
        return "🏆 Excellent"
    if sharpe >= 1.0:
        return "✅ Good"
    if sharpe >= 0.5:
        return "🔵 Fair"
    if sharpe >= 0.0:
        return "⚠️ Weak"
    return "❌ Negative"


def mdd_badge(mdd: float) -> str:
    pct = mdd * 100
    if pct > -5:
        return "🟢 Minimal"
    if pct > -15:
        return "🟡 Moderate"
    if pct > -30:
        return "🟠 Significant"
    return "🔴 Severe"


def var_badge(var: float) -> str:
    pct = var * 100
    if pct > -1:
        return "🟢 Low"
    if pct > -2.5:
        return "🟡 Moderate"
    if pct > -5:
        return "🟠 High"
    return "🔴 Very High"


# ── Markdown table ──────────────────────────────────────────────────────────

def format_risk_table(metrics: Dict[str, Any]) -> str:
    """
    Render a single ticker's risk metrics as a Markdown 2-column table.

    Guard against None values (e.g. from failed fetches) using (v or 0).
    """
    t = metrics
    ann_ret  = (t.get("ann_return")    or 0.0)
    ann_vol  = (t.get("ann_volatility") or 0.0)
    sharpe   = (t.get("sharpe")        or 0.0)
    sortino  = (t.get("sortino")       or 0.0)
    mdd      = (t.get("max_drawdown")  or 0.0)
    var95    = (t.get("var_95")        or 0.0)
    calmar   = (t.get("calmar")        or 0.0)
    rfr      = (t.get("risk_free_rate") or 0.05)
    rows = [
        ("Period (days)",          str(t.get("period_days", "—"))),
        ("Annualised Return",      f"{ann_ret*100:+.2f} %"),
        ("Annualised Volatility",  f"{ann_vol*100:.2f} %"),
        ("Sharpe Ratio",           f"{sharpe:.3f}  {sharpe_badge(sharpe)}"),
        ("Sortino Ratio",          f"{sortino:.3f}"),
        ("Max Drawdown",           f"{mdd*100:.2f} %  {mdd_badge(mdd)}"),
        ("VaR 95 % (1-day)",       f"{var95*100:.2f} %  {var_badge(var95)}"),
        ("Calmar Ratio",           f"{calmar:.3f}"),
        ("Risk Level",             risk_label_emoji(t.get("risk_label", "—"))),
        ("Risk-Free Rate",         f"{rfr*100:.1f} %"),
    ]
    header = (
        f"### 📊 Risk Metrics — {t.get('ticker', '—')}\n\n"
        "| Metric | Value |\n"
        "|--------|-------|"
    )
    lines = [header] + [f"| {k} | {v} |" for k, v in rows]
    return "\n".join(lines)


def format_multi_risk_table(metrics_list: List[Dict[str, Any]]) -> str:
    """
    Render a side-by-side comparison table for multiple tickers.
    """
    if not metrics_list:
        return "_No risk data._"

    tickers = [m.get("ticker", "—") for m in metrics_list]
    header = "| Metric | " + " | ".join(tickers) + " |\n"
    sep    = "|--------|" + "--------|" * len(tickers)

    def row(label: str, key: str, fmt: str) -> str:
        vals = []
        for m in metrics_list:
            v = m.get(key, 0)
            try:
                vals.append(fmt.format(v))
            except Exception:
                vals.append(str(v))
        return f"| {label} | " + " | ".join(vals) + " |"

    rows = [
        row("Ann. Return",      "ann_return",      "{:+.2%}"),
        row("Ann. Volatility",  "ann_volatility",  "{:.2%}"),
        row("Sharpe",           "sharpe",          "{:.3f}"),
        row("Sortino",          "sortino",          "{:.3f}"),
        row("Max Drawdown",     "max_drawdown",    "{:.2%}"),
        row("VaR 95%",          "var_95",          "{:.2%}"),
        row("Calmar",           "calmar",          "{:.3f}"),
        row("Risk Level",       "risk_label",      "{}"),
    ]
    return f"### 📊 Risk Metrics Comparison\n\n{header}{sep}\n" + "\n".join(rows)


def risk_metrics_to_dict(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten metrics to simple types for Streamlit DataFrame.

    Guards against None values with (v or 0) to prevent TypeError.
    """
    return {
        "Ticker":        metrics.get("ticker", ""),
        "Ann Return %":  round((metrics.get("ann_return")    or 0.0) * 100, 2),
        "Volatility %":  round((metrics.get("ann_volatility") or 0.0) * 100, 2),
        "Sharpe":        (metrics.get("sharpe")       or 0.0),
        "Sortino":       (metrics.get("sortino")      or 0.0),
        "Max DD %":      round((metrics.get("max_drawdown")  or 0.0) * 100, 2),
        "VaR 95% %":     round((metrics.get("var_95")        or 0.0) * 100, 2),
        "Calmar":        (metrics.get("calmar")       or 0.0),
        "Risk Level":    metrics.get("risk_label", ""),
    }
