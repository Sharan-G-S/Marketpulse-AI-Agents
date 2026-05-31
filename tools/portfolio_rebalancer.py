"""
Portfolio Allocation and Rebalancing Engine for MarketPulse.

Calculates current position deviations from a user-defined target allocation,
and computes trade instructions (buys/sells) to rebalance the portfolio.

No LLM required — pure mathematics.
"""

from typing import Any, Dict, List, Optional
