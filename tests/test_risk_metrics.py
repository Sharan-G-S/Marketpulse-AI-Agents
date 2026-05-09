"""
Unit Tests — tools/risk_metrics.py
"""

import importlib.util
import math
import os
import sys

import pytest

# Load directly from file to avoid circular imports via tools/__init__
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

_spec = importlib.util.spec_from_file_location(
    "tools.risk_metrics",
    os.path.join(_REPO, "tools", "risk_metrics.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

compute_daily_returns  = _mod.compute_daily_returns
annualised_return      = _mod.annualised_return
annualised_volatility  = _mod.annualised_volatility
sharpe_ratio           = _mod.sharpe_ratio
sortino_ratio          = _mod.sortino_ratio
max_drawdown           = _mod.max_drawdown
value_at_risk_95       = _mod.value_at_risk_95
calmar_ratio           = _mod.calmar_ratio
risk_label             = _mod.risk_label
compute_risk_metrics   = _mod.compute_risk_metrics

# ── Fixtures ────────────────────────────────────────────────────────────────

FLAT_HISTORY = [{"close": 100.0} for _ in range(10)]

RISING_HISTORY = [{"close": 100.0 + i * 2} for i in range(20)]

VOLATILE_HISTORY = [
    {"close": 100.0 + (10 if i % 2 == 0 else -10)}
    for i in range(30)
]

FALLING_HISTORY = [{"close": 200.0 - i * 3} for i in range(20)]


# ── compute_daily_returns ────────────────────────────────────────────────────

class TestComputeDailyReturns:
    def test_empty(self):
        assert compute_daily_returns([]) == []

    def test_single(self):
        assert compute_daily_returns([{"close": 100.0}]) == []

    def test_two_records(self):
        r = compute_daily_returns([{"close": 100.0}, {"close": 110.0}])
        assert len(r) == 1
        assert abs(r[0] - 0.10) < 1e-9

    def test_flat_returns_zero(self):
        rets = compute_daily_returns(FLAT_HISTORY)
        assert all(r == 0.0 for r in rets)

    def test_rising_positive(self):
        rets = compute_daily_returns(RISING_HISTORY)
        assert all(r > 0 for r in rets)

    def test_length_n_minus_1(self):
        rets = compute_daily_returns(RISING_HISTORY)
        assert len(rets) == len(RISING_HISTORY) - 1


# ── annualised_return ────────────────────────────────────────────────────────

class TestAnnualisedReturn:
    def test_empty_returns_zero(self):
        assert annualised_return([]) == 0.0

    def test_positive_returns(self):
        rets = compute_daily_returns(RISING_HISTORY)
        ar = annualised_return(rets)
        assert ar > 0

    def test_negative_returns(self):
        rets = compute_daily_returns(FALLING_HISTORY)
        ar = annualised_return(rets)
        assert ar < 0


# ── annualised_volatility ────────────────────────────────────────────────────

class TestAnnualisedVolatility:
    def test_flat_zero_vol(self):
        rets = compute_daily_returns(FLAT_HISTORY)
        assert annualised_volatility(rets) == 0.0

    def test_volatile_higher_than_stable(self):
        vol_v = annualised_volatility(compute_daily_returns(VOLATILE_HISTORY))
        vol_r = annualised_volatility(compute_daily_returns(RISING_HISTORY))
        assert vol_v > vol_r

    def test_positive_value(self):
        vol = annualised_volatility(compute_daily_returns(RISING_HISTORY))
        assert vol >= 0.0


# ── sharpe_ratio ─────────────────────────────────────────────────────────────

class TestSharpeRatio:
    def test_zero_vol_returns_zero(self):
        assert sharpe_ratio([], 0.05) == 0.0

    def test_falling_negative_sharpe(self):
        rets = compute_daily_returns(FALLING_HISTORY)
        assert sharpe_ratio(rets) < 0

    def test_rising_positive_sharpe(self):
        rets = compute_daily_returns(RISING_HISTORY)
        assert sharpe_ratio(rets) > 0


# ── max_drawdown ─────────────────────────────────────────────────────────────

class TestMaxDrawdown:
    def test_rising_history_small_mdd(self):
        mdd = max_drawdown(RISING_HISTORY)
        assert mdd == 0.0  # monotonically rising → no drawdown

    def test_falling_history_large_mdd(self):
        mdd = max_drawdown(FALLING_HISTORY)
        assert mdd < -0.1

    def test_mdd_non_positive(self):
        mdd = max_drawdown(VOLATILE_HISTORY)
        assert mdd <= 0.0

    def test_short_history(self):
        assert max_drawdown([{"close": 100.0}]) == 0.0


# ── value_at_risk_95 ──────────────────────────────────────────────────────────

class TestValueAtRisk:
    def test_empty(self):
        assert value_at_risk_95([]) == 0.0

    def test_var_non_positive_for_volatile(self):
        rets = compute_daily_returns(VOLATILE_HISTORY)
        var = value_at_risk_95(rets)
        assert var <= 0.0

    def test_rising_var_close_to_zero(self):
        rets = compute_daily_returns(RISING_HISTORY)
        var = value_at_risk_95(rets)
        # All returns positive → VaR should be non-negative or very small
        assert var >= -0.05


# ── compute_risk_metrics ──────────────────────────────────────────────────────

class TestComputeRiskMetrics:
    def test_returns_dict(self):
        result = compute_risk_metrics(RISING_HISTORY, ticker="AAPL")
        assert isinstance(result, dict)

    def test_ticker_uppercased(self):
        result = compute_risk_metrics(RISING_HISTORY, ticker="aapl")
        assert result["ticker"] == "AAPL"

    def test_all_keys_present(self):
        result = compute_risk_metrics(RISING_HISTORY, "AAPL")
        keys = {"ticker", "period_days", "ann_return", "ann_volatility",
                "sharpe", "sortino", "max_drawdown", "var_95", "calmar",
                "risk_label", "risk_free_rate"}
        assert keys.issubset(result.keys())

    def test_period_days(self):
        result = compute_risk_metrics(RISING_HISTORY, "AAPL")
        assert result["period_days"] == len(RISING_HISTORY)

    def test_risk_label_in_valid_set(self):
        result = compute_risk_metrics(VOLATILE_HISTORY, "TEST")
        assert result["risk_label"] in {"Low", "Moderate", "High", "Very High"}

    def test_rising_is_low_risk(self):
        result = compute_risk_metrics(RISING_HISTORY, "UP")
        assert result["risk_label"] in {"Low", "Moderate"}
