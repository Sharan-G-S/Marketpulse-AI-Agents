"""
Unit Tests — v1.7.0 new tool modules:
  tools/diversification_scorer.py
  tools/earnings_surprise.py
  tools/ma_crossover.py
  tools/data_quality.py
"""

import importlib.util
import math
import os
import sys

import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_REPO, relpath))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_div = _load("diversification_scorer", "tools/diversification_scorer.py")
_ear = _load("earnings_surprise",      "tools/earnings_surprise.py")
_mac = _load("ma_crossover",           "tools/ma_crossover.py")
_dq  = _load("data_quality",          "tools/data_quality.py")

# ── Diversification Scorer ────────────────────────────────────────────────────

compute_hhi        = _div.compute_hhi
sector_entropy     = _div.sector_entropy
score_diversification = _div.score_diversification


class TestComputeHHI:
    def test_single_stock(self):
        assert compute_hhi([1.0]) == pytest.approx(1.0)

    def test_equal_weights(self):
        # 4 equal weights → HHI = 4 × (0.25)² = 0.25
        assert compute_hhi([0.25, 0.25, 0.25, 0.25]) == pytest.approx(0.25)

    def test_empty_returns_one(self):
        assert compute_hhi([]) == 1.0

    def test_more_stocks_lower_hhi(self):
        h5  = compute_hhi([0.2] * 5)
        h10 = compute_hhi([0.1] * 10)
        assert h10 < h5

    def test_zero_total_returns_one(self):
        assert compute_hhi([0.0, 0.0]) == 1.0


class TestSectorEntropy:
    def test_single_sector_zero_entropy(self):
        assert sector_entropy({"Tech": 1000.0}) == 0.0

    def test_equal_sectors_max_entropy(self):
        sw = {"Tech": 100.0, "Finance": 100.0, "Health": 100.0}
        e = sector_entropy(sw)
        assert e == pytest.approx(1.0, abs=1e-6)

    def test_empty_returns_zero(self):
        assert sector_entropy({}) == 0.0

    def test_entropy_between_0_and_1(self):
        sw = {"Tech": 600.0, "Finance": 200.0, "Health": 200.0}
        e = sector_entropy(sw)
        assert 0.0 < e < 1.0


class TestScoreDiversification:
    POSITIONS_DIVERSE = [
        {"ticker": "AAPL", "market_value": 250.0},
        {"ticker": "JPM",  "market_value": 250.0},
        {"ticker": "JNJ",  "market_value": 250.0},
        {"ticker": "XOM",  "market_value": 250.0},
        {"ticker": "NFLX", "market_value": 250.0},
    ]
    SECTOR_MAP = {
        "AAPL": "Tech", "JPM": "Finance", "JNJ": "Healthcare",
        "XOM": "Energy", "NFLX": "Comms",
    }

    def test_returns_dict(self):
        r = score_diversification(self.POSITIONS_DIVERSE, self.SECTOR_MAP)
        assert isinstance(r, dict)

    def test_grade_key_present(self):
        r = score_diversification(self.POSITIONS_DIVERSE, self.SECTOR_MAP)
        assert r["grade"] in ("A", "B", "C", "D", "F")

    def test_diverse_portfolio_higher_score(self):
        diverse = score_diversification(self.POSITIONS_DIVERSE, self.SECTOR_MAP)
        concentrated = score_diversification(
            [{"ticker": "AAPL", "market_value": 1000.0}],
            {"AAPL": "Tech"},
        )
        assert diverse["score"] > concentrated["score"]

    def test_empty_positions(self):
        r = score_diversification([])
        assert r["n_positions"] == 0
        assert r["score"] == 0.0

    def test_suggestions_list(self):
        r = score_diversification(self.POSITIONS_DIVERSE, self.SECTOR_MAP)
        assert isinstance(r["suggestions"], list)


# ── Earnings Surprise ─────────────────────────────────────────────────────────

compute_eps_surprise    = _ear.compute_eps_surprise
eps_verdict             = _ear.eps_verdict
compute_earnings_surprise = _ear.compute_earnings_surprise
earnings_trend          = _ear.earnings_trend
format_earnings_table   = _ear.format_earnings_table


class TestComputeEpsSurprise:
    def test_positive_surprise(self):
        pct, abs_ = compute_eps_surprise(1.10, 1.00)
        assert pct == pytest.approx(10.0)
        assert abs_ == pytest.approx(0.10)

    def test_negative_surprise(self):
        pct, _ = compute_eps_surprise(0.90, 1.00)
        assert pct == pytest.approx(-10.0)

    def test_zero_estimate_no_crash(self):
        pct, abs_ = compute_eps_surprise(1.0, 0.0)
        assert pct == 0.0
        assert abs_ == pytest.approx(1.0)

    def test_exact_match(self):
        pct, abs_ = compute_eps_surprise(1.5, 1.5)
        assert pct == pytest.approx(0.0)
        assert abs_ == pytest.approx(0.0)


class TestEpsVerdict:
    def test_strong_beat(self):
        assert "Strong Beat" in eps_verdict(6.0)

    def test_beat(self):
        assert "Beat" in eps_verdict(2.5)

    def test_meet(self):
        assert "Meet" in eps_verdict(0.5)

    def test_miss(self):
        assert "Miss" in eps_verdict(-2.0)

    def test_strong_miss(self):
        assert "Strong Miss" in eps_verdict(-8.0)


class TestComputeEarningsSurprise:
    RECORD = {
        "ticker": "aapl", "period": "Q1 2026",
        "reported_eps": 2.20, "estimated_eps": 2.00,
        "revenue_actual": 95e9, "revenue_estimate": 90e9,
    }

    def test_ticker_uppercase(self):
        r = compute_earnings_surprise(self.RECORD)
        assert r["ticker"] == "AAPL"

    def test_eps_surprise_pct(self):
        r = compute_earnings_surprise(self.RECORD)
        assert r["eps_surprise_pct"] == pytest.approx(10.0)

    def test_overall_verdict_present(self):
        r = compute_earnings_surprise(self.RECORD)
        assert r["overall_verdict"]

    def test_revenue_surprise_computed(self):
        r = compute_earnings_surprise(self.RECORD)
        assert r["revenue_surprise_pct"] is not None


class TestEarningsTrend:
    RESULTS = [
        {"eps_surprise_pct": 5.0},
        {"eps_surprise_pct": 3.0},
        {"eps_surprise_pct": -2.0},
        {"eps_surprise_pct": 7.0},
    ]

    def test_empty_returns_na(self):
        r = earnings_trend([])
        assert r["trend_label"] == "N/A"

    def test_beat_count(self):
        r = earnings_trend(self.RESULTS)
        assert r["beat_count"] == 3

    def test_avg_surprise_in_range(self):
        r = earnings_trend(self.RESULTS)
        assert -100 < r["avg_surprise_pct"] < 100


class TestFormatEarningsTable:
    def test_empty_returns_no_data_string(self):
        assert "No earnings" in format_earnings_table([])

    def test_returns_markdown_table(self):
        results = [compute_earnings_surprise({
            "ticker": "AAPL", "period": "Q1 2026",
            "reported_eps": 2.0, "estimated_eps": 1.8,
        })]
        table = format_earnings_table(results)
        assert "|" in table
        assert "AAPL" in table


# ── MA Crossover ──────────────────────────────────────────────────────────────

compute_sma      = _mac.compute_sma
compute_ema      = _mac.compute_ema
detect_crossovers = _mac.detect_crossovers
extract_closes   = _mac.extract_closes
ma_crossover_summary = _mac.ma_crossover_summary


class TestComputeSMA:
    def test_length_matches_input(self):
        prices = list(range(1, 11))
        sma = compute_sma(prices, 3)
        assert len(sma) == len(prices)

    def test_leading_nones(self):
        sma = compute_sma([1, 2, 3, 4, 5], period=3)
        assert sma[0] is None
        assert sma[1] is None
        assert sma[2] is not None

    def test_correct_value(self):
        sma = compute_sma([10.0, 20.0, 30.0], period=3)
        assert sma[-1] == pytest.approx(20.0)

    def test_period_1_equals_price(self):
        prices = [5.0, 10.0, 15.0]
        sma = compute_sma(prices, 1)
        assert sma == prices


class TestComputeEMA:
    def test_length_matches_input(self):
        prices = [float(i) for i in range(1, 21)]
        ema = compute_ema(prices, 5)
        assert len(ema) == len(prices)

    def test_insufficient_data_all_none(self):
        ema = compute_ema([1.0, 2.0], period=10)
        assert all(v is None for v in ema)

    def test_ema_responds_to_recent_prices(self):
        # Rising prices → EMA should be below latest price (lagged)
        prices = [100.0 + i for i in range(20)]
        ema = compute_ema(prices, 5)
        last_ema = next(v for v in reversed(ema) if v is not None)
        assert last_ema < prices[-1]


class TestDetectCrossovers:
    def test_golden_cross_detected(self):
        # fast goes from below to above slow
        fast = [None, 8.0, 12.0]
        slow = [None, 10.0, 10.0]
        events = detect_crossovers(fast, slow)
        assert any(e["signal"] == "Golden Cross" for e in events)

    def test_death_cross_detected(self):
        fast = [None, 12.0, 8.0]
        slow = [None, 10.0, 10.0]
        events = detect_crossovers(fast, slow)
        assert any(e["signal"] == "Death Cross" for e in events)

    def test_no_crossover_stable(self):
        fast = [5.0, 5.0, 5.0]
        slow = [10.0, 10.0, 10.0]
        events = detect_crossovers(fast, slow)
        assert events == []


class TestExtractCloses:
    def test_extracts_close_field(self):
        history = [{"close": 100.0}, {"close": 110.0}]
        assert extract_closes(history) == [100.0, 110.0]

    def test_extracts_Close_capitalised(self):
        history = [{"Close": 200.0}]
        assert extract_closes(history) == [200.0]

    def test_skips_none(self):
        history = [{"close": None}, {"close": 100.0}]
        assert extract_closes(history) == [100.0]

    def test_empty_input(self):
        assert extract_closes([]) == []


class TestMaCrossoverSummary:
    HISTORY = [{"close": float(100 + i)} for i in range(60)]

    def test_returns_dict(self):
        r = ma_crossover_summary(self.HISTORY, fast_period=5, slow_period=10)
        assert isinstance(r, dict)

    def test_insufficient_data(self):
        r = ma_crossover_summary([{"close": 100.0}], fast_period=50, slow_period=200)
        assert "Insufficient" in r["current_signal"]

    def test_bullish_signal_for_rising_prices(self):
        r = ma_crossover_summary(self.HISTORY, fast_period=5, slow_period=10)
        assert "Bullish" in r["current_signal"]


# ── Data Quality Validator ────────────────────────────────────────────────────

validate_bar            = _dq.validate_bar
validate_price_history  = _dq.validate_price_history
validate_stock_summary  = _dq.validate_stock_summary
format_validation_report = _dq.format_validation_report

GOOD_BAR    = {"open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1_000_000}
BAD_BAR_HL  = {"open": 100.0, "high": 90.0,  "low": 95.0, "close": 105.0}  # high < low


class TestValidateBar:
    def test_valid_bar_no_issues(self):
        issues = validate_bar(GOOD_BAR, 0)
        errors = [i for i in issues if i["level"] == "error"]
        assert errors == []

    def test_high_lt_low_is_error(self):
        issues = validate_bar(BAD_BAR_HL, 0)
        assert any(i["level"] == "error" for i in issues)

    def test_missing_field_is_error(self):
        bar = {"open": 100.0, "high": 110.0, "low": 95.0}  # missing close
        issues = validate_bar(bar, 0)
        assert any("close" in i["field"] and i["level"] == "error" for i in issues)

    def test_non_numeric_field_is_error(self):
        bar = {**GOOD_BAR, "close": "N/A"}
        issues = validate_bar(bar, 0)
        assert any(i["level"] == "error" for i in issues)


class TestValidatePriceHistory:
    def test_empty_history_invalid(self):
        r = validate_price_history([])
        assert r["valid"] is False
        assert r["errors"] >= 1

    def test_good_history_valid(self):
        history = [GOOD_BAR] * 10
        r = validate_price_history(history)
        assert r["valid"] is True

    def test_score_between_0_and_100(self):
        r = validate_price_history([GOOD_BAR] * 5)
        assert 0 <= r["score"] <= 100

    def test_too_few_bars_warning(self):
        r = validate_price_history([GOOD_BAR] * 2, min_bars=5)
        assert r["warnings"] >= 1


class TestValidateStockSummary:
    GOOD_SUMMARY = {
        "ticker": "AAPL", "current_price": 175.0,
        "change_pct": 1.5, "volume": 5_000_000,
    }

    def test_good_summary_valid(self):
        r = validate_stock_summary(self.GOOD_SUMMARY)
        assert r["valid"] is True

    def test_missing_ticker_invalid(self):
        r = validate_stock_summary({"current_price": 100.0})
        assert r["valid"] is False

    def test_extreme_change_pct_warning(self):
        r = validate_stock_summary({**self.GOOD_SUMMARY, "change_pct": 75.0})
        assert r["warnings"] >= 1

    def test_negative_price_warning(self):
        r = validate_stock_summary({**self.GOOD_SUMMARY, "current_price": -5.0})
        assert r["warnings"] >= 1 or r["errors"] >= 1


class TestFormatValidationReport:
    def test_returns_string(self):
        r = validate_stock_summary({"ticker": "AAPL", "current_price": 100.0})
        out = format_validation_report(r, "AAPL Summary")
        assert isinstance(out, str)

    def test_contains_score(self):
        r = validate_price_history([GOOD_BAR] * 5)
        out = format_validation_report(r, "Test")
        assert "Score" in out or "score" in out.lower()
