"""
MarketPulse — Forex & Multi-Currency Normalization Engine
Normalizes international stock prices and portfolio valuations across major currencies.
"""

from typing import Dict

# Static FX exchange rate lookup matrix (relative to USD)
STATIC_FX_RATES: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "JPY": 0.0065,
    "CAD": 0.74,
    "AUD": 0.65,
    "INR": 0.012,
}


def convert_currency(amount: float, from_curr: str = "USD", to_curr: str = "USD") -> float:
    """
    Converts monetary amount from one currency to another using exchange rates.

    Args:
        amount: Numeric amount to convert
        from_curr: Source currency ISO code (e.g. "EUR")
        to_curr: Target currency ISO code (e.g. "USD")

    Returns:
        Converted amount float.
    """
    if not amount or amount <= 0:
        return 0.0

    from_c = from_curr.upper()
    to_c = to_curr.upper()

    if from_c == to_c:
        return round(amount, 2)

    from_rate = STATIC_FX_RATES.get(from_c, 1.0)
    to_rate = STATIC_FX_RATES.get(to_c, 1.0)

    # Convert source -> USD -> target
    amount_usd = amount * from_rate
    converted = amount_usd / to_rate

    return round(converted, 2)
