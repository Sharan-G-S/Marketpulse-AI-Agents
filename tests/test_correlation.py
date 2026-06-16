"""Unit tests for tools/correlation.py portfolio correlation analysis."""

from tools.correlation import (
    compute_correlation_matrix,
    compute_rolling_correlation,
    correlation_label,
    format_correlation_report,
)


def _make_history(closes):
    """Create minimal OHLCV records from a list of closing prices."""
    return [{"close": c, "volume": 1000} for c in closes]


# ── compute_correlation_matrix ────────────────────────────────────────────────

class TestComputeCorrelationMatrix:
    def test_self_correlation_is_one(self):
        hist = _make_history([10.0, 11.0, 12.0, 11.5, 13.0])
        matrix = compute_correlation_matrix({"AAPL": hist})
        assert matrix["AAPL"]["AAPL"] == 1.0

    def test_perfect_positive_correlation(self):
        closes = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
        hist = _make_history(closes)
        matrix = compute_correlation_matrix({"A": hist, "B": hist})
        assert matrix["A"]["B"] == 1.0

    def test_negative_correlation_direction(self):
        # Alternating: A goes up when B goes down and vice versa → negative correlation
        closes_a = [10.0, 12.0, 10.0, 12.0, 10.0, 12.0, 10.0, 12.0, 10.0, 12.0]
        closes_b = [12.0, 10.0, 12.0, 10.0, 12.0, 10.0, 12.0, 10.0, 12.0, 10.0]
        hist_a = _make_history(closes_a)
        hist_b = _make_history(closes_b)
        matrix = compute_correlation_matrix({"A": hist_a, "B": hist_b})
        assert matrix["A"]["B"] is not None
        assert matrix["A"]["B"] < 0  # should be negative

    def test_empty_history_returns_none(self):
        matrix = compute_correlation_matrix({"A": [], "B": []})
        assert matrix["A"]["B"] is None

    def test_single_bar_history_returns_none(self):
        hist = _make_history([100.0])
        matrix = compute_correlation_matrix({"A": hist, "B": hist})
        assert matrix["A"]["B"] is None

    def test_symmetry(self):
        hist_a = _make_history([10.0, 12.0, 11.0, 13.0, 14.0])
        hist_b = _make_history([20.0, 19.0, 21.0, 22.0, 20.0])
        matrix = compute_correlation_matrix({"A": hist_a, "B": hist_b})
        assert matrix["A"]["B"] == matrix["B"]["A"]

    def test_multiple_tickers(self):
        hist_a = _make_history([10.0, 11.0, 12.0, 11.5, 13.0])
        hist_b = _make_history([20.0, 21.0, 20.5, 22.0, 21.0])
        hist_c = _make_history([5.0, 4.5, 5.5, 6.0, 5.8])
        matrix = compute_correlation_matrix({"A": hist_a, "B": hist_b, "C": hist_c})
        assert "A" in matrix and "B" in matrix and "C" in matrix
        assert matrix["A"]["A"] == 1.0
        assert matrix["B"]["B"] == 1.0


# ── compute_rolling_correlation ───────────────────────────────────────────────

class TestComputeRollingCorrelation:
    def test_empty_returns_empty(self):
        result = compute_rolling_correlation([], [])
        assert result == []

    def test_warmup_period_is_none(self):
        hist = _make_history([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
        result = compute_rolling_correlation(hist, hist, window=5)
        # first (window-1) entries must be None
        for _idx, corr in result[:4]:
            assert corr is None

    def test_same_series_gives_one(self):
        closes = [10.0, 11.0, 10.5, 12.0, 13.0, 12.5, 14.0, 15.0, 14.5, 16.0,
                  17.0, 16.5, 18.0, 19.0, 18.5, 20.0, 21.0, 20.5, 22.0, 23.0,
                  24.0, 25.0]
        hist = _make_history(closes)
        result = compute_rolling_correlation(hist, hist, window=10)
        for _, corr in result:
            if corr is not None:
                assert abs(corr - 1.0) < 1e-6

    def test_result_length_matches_returns(self):
        hist_a = _make_history([10.0 + i for i in range(25)])
        hist_b = _make_history([20.0 - i * 0.5 for i in range(25)])
        result = compute_rolling_correlation(hist_a, hist_b, window=5)
        # rolling correlation is computed on returns so length = min(n)-1
        assert len(result) == 24


# ── correlation_label ─────────────────────────────────────────────────────────

class TestCorrelationLabel:
    def test_none_returns_na(self):
        assert correlation_label(None) == "N/A"

    def test_strong_positive(self):
        assert correlation_label(0.9) == "Strong Positive"

    def test_moderate_positive(self):
        assert correlation_label(0.5) == "Moderate Positive"

    def test_weak(self):
        assert correlation_label(0.0) == "Weak / No Correlation"

    def test_moderate_negative(self):
        assert correlation_label(-0.5) == "Moderate Negative"

    def test_strong_negative(self):
        assert correlation_label(-0.9) == "Strong Negative"

    def test_boundary_positive_07(self):
        assert correlation_label(0.7) == "Strong Positive"

    def test_boundary_negative_07(self):
        assert correlation_label(-0.7) == "Strong Negative"


# ── format_correlation_report ─────────────────────────────────────────────────

class TestFormatCorrelationReport:
    def test_empty_matrix_returns_placeholder(self):
        assert "_No correlation data available._" in format_correlation_report({})

    def test_single_ticker_shows_self(self):
        matrix = {"AAPL": {"AAPL": 1.0}}
        report = format_correlation_report(matrix)
        assert "AAPL" in report
        assert "1.00" in report

    def test_report_contains_tickers(self):
        matrix = {
            "AAPL": {"AAPL": 1.0, "MSFT": 0.75},
            "MSFT": {"AAPL": 0.75, "MSFT": 1.0},
        }
        report = format_correlation_report(matrix)
        assert "AAPL" in report
        assert "MSFT" in report

    def test_custom_title(self):
        matrix = {"X": {"X": 1.0}}
        report = format_correlation_report(matrix, title="My Test Matrix")
        assert "My Test Matrix" in report

    def test_none_values_show_na(self):
        matrix = {"A": {"A": 1.0, "B": None}, "B": {"A": None, "B": 1.0}}
        report = format_correlation_report(matrix)
        assert "N/A" in report
