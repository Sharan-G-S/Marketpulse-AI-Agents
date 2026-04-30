import importlib.util
import os
import sys

import pytest

# Import alert_engine directly from file to bypass agents/__init__.py
# (which triggers a circular import chain via graph/workflow.py)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

_spec = importlib.util.spec_from_file_location(
    "agents.alert_engine",
    os.path.join(_REPO_ROOT, "agents", "alert_engine.py"),
)
_alert_engine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_alert_engine)

evaluate_alerts = _alert_engine.evaluate_alerts
format_alert_summary = _alert_engine.format_alert_summary
get_alert_severity_counts = _alert_engine.get_alert_severity_counts
has_critical_alerts = _alert_engine.has_critical_alerts
DEFAULT_THRESHOLDS = _alert_engine.DEFAULT_THRESHOLDS
SEVERITY_CRITICAL = _alert_engine.SEVERITY_CRITICAL
SEVERITY_WARNING = _alert_engine.SEVERITY_WARNING
SEVERITY_INFO = _alert_engine.SEVERITY_INFO

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

BASE_STATE = {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "analysis_depth": "standard",
    "overall_sentiment": "Neutral",
    "sentiment_confidence": 0.8,
    "stock_summary": {
        "current_price": 188.0,
        "change_pct": 1.2,
    },
    "risk_level": "Medium",
    "risk_flags": ["Rising competition"],
    "messages": [],
    "error": None,
}


# ---------------------------------------------------------------------------
# TestEvaluateAlerts
# ---------------------------------------------------------------------------


class TestEvaluateAlerts:
    def test_no_alerts_for_normal_state(self):
        """A healthy state with no thresholds breached should return zero alerts."""
        alerts = evaluate_alerts(BASE_STATE)
        assert isinstance(alerts, list)
        assert len(alerts) == 0

    def test_high_risk_level_triggers_warning(self):
        """High risk_level should generate a WARNING alert."""
        state = {**BASE_STATE, "risk_level": "High"}
        alerts = evaluate_alerts(state)
        types = [a["alert_type"] for a in alerts]
        assert "RISK_LEVEL" in types
        risk_alert = next(a for a in alerts if a["alert_type"] == "RISK_LEVEL")
        assert risk_alert["severity"] == SEVERITY_WARNING

    def test_critical_risk_level_triggers_critical(self):
        """Critical risk_level should generate a CRITICAL severity alert."""
        state = {**BASE_STATE, "risk_level": "Critical"}
        alerts = evaluate_alerts(state)
        risk_alert = next(a for a in alerts if a["alert_type"] == "RISK_LEVEL")
        assert risk_alert["severity"] == SEVERITY_CRITICAL

    def test_large_price_drop_triggers_alert(self):
        """A price drop >= threshold should create a PRICE_MOVE alert."""
        state = {
            **BASE_STATE,
            "stock_summary": {"current_price": 150.0, "change_pct": -7.5},
        }
        alerts = evaluate_alerts(state)
        types = [a["alert_type"] for a in alerts]
        assert "PRICE_MOVE" in types
        move_alert = next(a for a in alerts if a["alert_type"] == "PRICE_MOVE")
        assert move_alert["value"] == -7.5

    def test_large_price_surge_triggers_alert(self):
        """A price surge >= threshold should create a PRICE_MOVE alert."""
        state = {
            **BASE_STATE,
            "stock_summary": {"current_price": 210.0, "change_pct": 8.3},
        }
        alerts = evaluate_alerts(state)
        types = [a["alert_type"] for a in alerts]
        assert "PRICE_MOVE" in types

    def test_many_risk_flags_triggers_alert(self):
        """Having >= min_risk_flags should trigger a RISK_FLAG_COUNT alert."""
        state = {
            **BASE_STATE,
            "risk_flags": ["Flag A", "Flag B", "Flag C", "Flag D"],
        }
        alerts = evaluate_alerts(state)
        types = [a["alert_type"] for a in alerts]
        assert "RISK_FLAG_COUNT" in types

    def test_low_sentiment_confidence_triggers_info(self):
        """Confidence below threshold should generate an INFO alert."""
        state = {**BASE_STATE, "sentiment_confidence": 0.2}
        alerts = evaluate_alerts(state)
        types = [a["alert_type"] for a in alerts]
        assert "LOW_SENTIMENT_CONFIDENCE" in types
        info_alert = next(a for a in alerts if a["alert_type"] == "LOW_SENTIMENT_CONFIDENCE")
        assert info_alert["severity"] == SEVERITY_INFO

    def test_bearish_high_risk_combo_triggers_critical(self):
        """Bearish sentiment + High risk should trigger a BEARISH_HIGH_RISK CRITICAL alert."""
        state = {
            **BASE_STATE,
            "overall_sentiment": "Bearish",
            "risk_level": "High",
        }
        alerts = evaluate_alerts(state)
        types = [a["alert_type"] for a in alerts]
        assert "BEARISH_HIGH_RISK" in types
        combo = next(a for a in alerts if a["alert_type"] == "BEARISH_HIGH_RISK")
        assert combo["severity"] == SEVERITY_CRITICAL

    def test_alert_has_required_keys(self):
        """Every alert must contain all required metadata keys."""
        state = {**BASE_STATE, "risk_level": "High"}
        alerts = evaluate_alerts(state)
        required_keys = {"alert_type", "severity", "message", "value", "threshold", "ticker", "timestamp"}
        for alert in alerts:
            assert required_keys.issubset(alert.keys()), f"Missing keys: {required_keys - alert.keys()}"

    def test_custom_threshold_override(self):
        """Custom thresholds should override defaults."""
        state = {
            **BASE_STATE,
            "stock_summary": {"current_price": 190.0, "change_pct": 3.0},
        }
        # Default threshold is 5.0 — this should NOT trigger
        alerts_default = evaluate_alerts(state)
        price_alerts_default = [a for a in alerts_default if a["alert_type"] == "PRICE_MOVE"]
        assert len(price_alerts_default) == 0

        # Override threshold to 2.0 — this SHOULD trigger
        alerts_custom = evaluate_alerts(state, thresholds={"price_change_pct": 2.0})
        price_alerts_custom = [a for a in alerts_custom if a["alert_type"] == "PRICE_MOVE"]
        assert len(price_alerts_custom) == 1

    def test_ticker_included_in_alerts(self):
        """Each alert should reference the correct ticker."""
        state = {**BASE_STATE, "ticker": "TSLA", "risk_level": "High"}
        alerts = evaluate_alerts(state)
        for alert in alerts:
            assert alert["ticker"] == "TSLA"


# ---------------------------------------------------------------------------
# TestFormatAlertSummary
# ---------------------------------------------------------------------------


class TestFormatAlertSummary:
    def test_empty_alerts_returns_empty_string(self):
        assert format_alert_summary([]) == ""

    def test_summary_contains_ticker(self):
        state = {**BASE_STATE, "risk_level": "High"}
        alerts = evaluate_alerts(state)
        summary = format_alert_summary(alerts)
        assert "AAPL" in summary

    def test_summary_contains_section_headers(self):
        state = {**BASE_STATE, "overall_sentiment": "Bearish", "risk_level": "Critical"}
        alerts = evaluate_alerts(state)
        summary = format_alert_summary(alerts)
        assert "CRITICAL" in summary
        assert "MarketPulse Alert Report" in summary


# ---------------------------------------------------------------------------
# TestHelpers
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_get_alert_severity_counts_empty(self):
        counts = get_alert_severity_counts([])
        assert counts[SEVERITY_CRITICAL] == 0
        assert counts[SEVERITY_WARNING] == 0
        assert counts[SEVERITY_INFO] == 0

    def test_get_alert_severity_counts_mixed(self):
        state = {
            **BASE_STATE,
            "risk_level": "Critical",
            "overall_sentiment": "Bearish",
            "sentiment_confidence": 0.1,
        }
        alerts = evaluate_alerts(state)
        counts = get_alert_severity_counts(alerts)
        assert counts[SEVERITY_CRITICAL] >= 1

    def test_has_critical_alerts_true(self):
        state = {**BASE_STATE, "risk_level": "Critical"}
        alerts = evaluate_alerts(state)
        assert has_critical_alerts(alerts) is True

    def test_has_critical_alerts_false(self):
        alerts = evaluate_alerts(BASE_STATE)
        assert has_critical_alerts(alerts) is False
