"""
Unit tests for tools/forex_converter.py
"""

from tools.forex_converter import convert_currency


def test_convert_currency_same():
    assert convert_currency(100.0, "USD", "USD") == 100.0


def test_convert_currency_eur_to_usd():
    # 100 EUR @ 1.08 = 108 USD
    res = convert_currency(100.0, "EUR", "USD")
    assert res == 108.0


def test_convert_currency_usd_to_eur():
    # 108 USD / 1.08 = 100 EUR
    res = convert_currency(108.0, "USD", "EUR")
    assert res == 100.0
