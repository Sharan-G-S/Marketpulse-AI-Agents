# MarketPulse AI — Enterprise API Reference & Developer Guide

This document details core tool interfaces, mathematical algorithms, and state models in **MarketPulse AI Agents**.

---

## 🛠️ Analytics Tool Reference

### 1. Options Pricing (`tools/options_pricing.py`)
- `calculate_black_scholes(stock_price, strike_price, time_to_expiry_years, risk_free_rate, volatility)`: Returns Call/Put theoretical prices and Delta.

### 2. Bond Yield Curve (`tools/bond_yield_curve.py`)
- `calculate_bond_metrics(face_value, coupon_rate_pct, years_to_maturity, current_bond_price)`: Returns Yield to Maturity (YTM) and Macaulay Duration.

### 3. REIT Valuation (`tools/reit_calculator.py`)
- `calculate_reit_valuation(share_price, net_operating_income, property_value, ffo_per_share, dividend_per_share)`: Returns Cap Rate %, P/FFO multiple, and dividend yield.

### 4. Capital Allocation (`tools/roic_calculator.py`)
- `calculate_roic_efficiency(nopat, total_debt, total_equity, cash, wacc_pct)`: Returns ROIC % vs WACC spread.

---

## 🤖 State Graph Definition

```python
class MarketPulseState(TypedDict):
    ticker: str
    company_name: str
    analysis_depth: str
    raw_news: List[Dict[str, Any]]
    stock_summary: Dict[str, Any]
    price_history: List[Dict[str, Any]]
    sentiment_scores: List[Dict[str, Any]]
    overall_sentiment: str
    risk_level: str
    final_report: str
```
