"""
Unit Tests — tools/portfolio_performance.py and tools/news_digest.py
and tools/market_calendar.py
"""

from datetime import date, timedelta
import importlib.util
import os
import sys

import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_REPO, relpath))
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_pp  = _load("portfolio_performance", "tools/portfolio_performance.py")
_nd  = _load("news_digest",           "tools/news_digest.py")
_mc  = _load("market_calendar",       "tools/market_calendar.py")

compute_position   = _pp.compute_position
compute_portfolio  = _pp.compute_portfolio
top_holdings       = _pp.top_holdings
sector_allocation  = _pp.sector_allocation

deduplicate_articles       = _nd.deduplicate_articles
rank_articles              = _nd.rank_articles
build_digest_entries       = _nd.build_digest_entries
format_news_digest_markdown = _nd.format_news_digest_markdown
digest_sentiment_summary   = _nd.digest_sentiment_summary

extract_earnings_date  = _mc.extract_earnings_date
build_ticker_events    = _mc.build_ticker_events
build_market_calendar  = _mc.build_market_calendar
format_calendar_markdown = _mc.format_calendar_markdown
upcoming_earnings_list = _mc.upcoming_earnings_list


# ────────────────────────────────────────────────────────────────────────────
# Portfolio Performance Tests
# ────────────────────────────────────────────────────────────────────────────

class TestComputePosition:
    def test_basic_gain(self):
        pos = {"ticker": "AAPL", "qty": 10, "avg_cost": 100.0}
        r = compute_position(pos, 120.0, total_market_value=1200.0)
        assert r["unrealised_pl"] == pytest.approx(200.0)
        assert r["unrealised_pct"] == pytest.approx(20.0)
        assert r["market_value"] == pytest.approx(1200.0)
        assert r["weight_pct"] == pytest.approx(100.0)

    def test_basic_loss(self):
        pos = {"ticker": "TSLA", "qty": 5, "avg_cost": 200.0}
        r = compute_position(pos, 150.0)
        assert r["unrealised_pl"] == pytest.approx(-250.0)
        assert r["unrealised_pct"] == pytest.approx(-25.0)

    def test_ticker_uppercase(self):
        r = compute_position({"ticker": "msft", "qty": 1, "avg_cost": 100.0}, 100.0)
        assert r["ticker"] == "MSFT"

    def test_zero_avg_cost_no_crash(self):
        r = compute_position({"ticker": "X", "qty": 1, "avg_cost": 0.0}, 50.0)
        assert r["unrealised_pct"] == 0.0


class TestComputePortfolio:
    POSITIONS = [
        {"ticker": "AAPL", "qty": 10, "avg_cost": 100.0},
        {"ticker": "MSFT", "qty": 5,  "avg_cost": 200.0},
    ]
    PRICES = {"AAPL": 120.0, "MSFT": 180.0}

    def test_returns_dict(self):
        r = compute_portfolio(self.POSITIONS, self.PRICES)
        assert isinstance(r, dict)

    def test_total_market_value(self):
        r = compute_portfolio(self.POSITIONS, self.PRICES)
        # 10×120 + 5×180 = 1200 + 900 = 2100
        assert r["total_market_value"] == pytest.approx(2100.0)

    def test_n_positions(self):
        r = compute_portfolio(self.POSITIONS, self.PRICES)
        assert r["n_positions"] == 2

    def test_empty_positions(self):
        r = compute_portfolio([], {})
        assert r["total_market_value"] == 0.0
        assert r["n_positions"] == 0

    def test_best_worst_keys_exist(self):
        r = compute_portfolio(self.POSITIONS, self.PRICES)
        assert "best_performer" in r
        assert "worst_performer" in r

    def test_missing_price_uses_avg_cost(self):
        r = compute_portfolio(self.POSITIONS, {})
        # No live price → uses avg_cost → P&L = 0
        assert r["total_unrealised_pl"] == pytest.approx(0.0)


class TestTopHoldings:
    def test_top_n_limit(self):
        positions = [{"ticker": f"T{i}", "qty": 1, "avg_cost": 1.0} for i in range(10)]
        summary = compute_portfolio(positions, {})
        result = top_holdings(summary, n=3)
        assert len(result) <= 3


class TestSectorAllocation:
    def test_groups_by_sector(self):
        positions = [
            {"ticker": "AAPL", "market_value": 500.0},
            {"ticker": "MSFT", "market_value": 300.0},
            {"ticker": "JPM",  "market_value": 200.0},
        ]
        sm = {"AAPL": "Tech", "MSFT": "Tech", "JPM": "Finance"}
        alloc = sector_allocation(positions, sm)
        assert alloc["Tech"] == pytest.approx(800.0)
        assert alloc["Finance"] == pytest.approx(200.0)

    def test_unknown_ticker_groups_to_other(self):
        positions = [{"ticker": "XYZ", "market_value": 100.0}]
        alloc = sector_allocation(positions, {})
        assert "Other" in alloc


# ────────────────────────────────────────────────────────────────────────────
# News Digest Tests
# ────────────────────────────────────────────────────────────────────────────

ARTICLES = [
    {"title": "Apple beats earnings", "sentiment": "Bullish", "score": 0.8,
     "publishedAt": "2026-05-10", "source": "Reuters", "url": "http://a.com"},
    {"title": "Apple beats earnings forecast", "sentiment": "Bullish", "score": 0.7,
     "publishedAt": "2026-05-10", "source": "Bloomberg", "url": "http://b.com"},
    {"title": "Market falls on Fed news", "sentiment": "Bearish", "score": -0.6,
     "publishedAt": "2026-05-09", "source": "CNBC", "url": "http://c.com"},
    {"title": "Tech stocks rally", "sentiment": "Bullish", "score": 0.5,
     "publishedAt": "2026-05-10", "source": "WSJ", "url": "http://d.com"},
]


class TestDeduplicateArticles:
    def test_removes_near_duplicate(self):
        result = deduplicate_articles(ARTICLES, threshold=0.55)
        # First two articles are very similar — one should be removed
        assert len(result) < len(ARTICLES)

    def test_keeps_unique_articles(self):
        result = deduplicate_articles(ARTICLES, threshold=0.99)
        # High threshold → almost nothing is a duplicate
        assert len(result) == len(ARTICLES)

    def test_empty_input(self):
        assert deduplicate_articles([]) == []


class TestRankArticles:
    def test_top_n_limit(self):
        result = rank_articles(ARTICLES, top_n=2)
        assert len(result) == 2

    def test_higher_abs_score_first(self):
        result = rank_articles(ARTICLES, top_n=4)
        scores = [abs(a.get("score", 0)) for a in result]
        assert scores == sorted(scores, reverse=True)


class TestBuildDigestEntries:
    def test_returns_list(self):
        entries = build_digest_entries(ARTICLES)
        assert isinstance(entries, list)
        assert len(entries) == len(ARTICLES)

    def test_entry_has_required_keys(self):
        entry = build_digest_entries(ARTICLES[:1])[0]
        for key in ("title", "source", "date", "url", "sentiment", "score", "snippet"):
            assert key in entry

    def test_snippet_truncated(self):
        long_art = [{"title": "T", "description": "x" * 200, "sentiment": "Neutral"}]
        entry = build_digest_entries(long_art)[0]
        assert len(entry["snippet"]) <= 165  # 160 + ellipsis


class TestDigestSentimentSummary:
    def test_counts(self):
        entries = build_digest_entries(ARTICLES)
        stats = digest_sentiment_summary(entries)
        assert stats["total"] == len(ARTICLES)
        assert stats["bullish_count"] + stats["bearish_count"] + stats["neutral_count"] == len(ARTICLES)

    def test_avg_score_in_range(self):
        entries = build_digest_entries(ARTICLES)
        stats = digest_sentiment_summary(entries)
        assert -1.0 <= stats["avg_score"] <= 1.0


# ────────────────────────────────────────────────────────────────────────────
# Market Calendar Tests
# ────────────────────────────────────────────────────────────────────────────

class TestExtractEarningsDate:
    def test_returns_none_when_missing(self):
        assert extract_earnings_date({}) is None

    def test_extracts_string_date(self):
        result = extract_earnings_date({"earningsDate": "2026-07-25"})
        assert result == "2026-07-25"

    def test_extracts_list_date(self):
        result = extract_earnings_date({"earningsDate": ["2026-07-25", "2026-07-26"]})
        assert result == "2026-07-25"


class TestBuildTickerEvents:
    def test_empty_summary_returns_empty(self):
        events = build_ticker_events("AAPL", {})
        assert events == []

    def test_past_earnings_not_included(self):
        # Past date should be filtered out
        events = build_ticker_events("AAPL", {"earningsDate": "2020-01-01"})
        assert not any(e["event_type"] == "earnings" for e in events)

    def test_future_earnings_included(self):
        future = (date.today() + timedelta(days=30)).isoformat()
        events = build_ticker_events("AAPL", {"earningsDate": future})
        assert any(e["event_type"] == "earnings" for e in events)


class TestBuildMarketCalendar:
    def test_includes_holidays(self):
        events = build_market_calendar({}, include_holidays=True, days_ahead=365)
        assert any(e["event_type"] == "holiday" for e in events)

    def test_excludes_holidays_when_false(self):
        events = build_market_calendar({}, include_holidays=False, days_ahead=365)
        assert not any(e["event_type"] == "holiday" for e in events)

    def test_sorted_by_date(self):
        events = build_market_calendar({}, include_holidays=True, days_ahead=365)
        dates = [e["date"] for e in events]
        assert dates == sorted(dates)


class TestFormatCalendarMarkdown:
    def test_empty_returns_no_events_string(self):
        result = format_calendar_markdown([])
        assert "No upcoming" in result

    def test_returns_markdown_table(self):
        future = (date.today() + timedelta(days=5)).isoformat()
        events = [{"date": future, "event_type": "earnings", "ticker": "AAPL",
                   "description": "AAPL Q earnings", "importance": "high"}]
        result = format_calendar_markdown(events)
        assert "|" in result
        assert "AAPL" in result
