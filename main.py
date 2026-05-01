"""
MarketPulse CLI Entry Point
Run a full analysis from the command line.

Usage:
    python main.py --ticker AAPL
    python main.py --ticker TSLA --depth deep
    python main.py --ticker MSFT --company "Microsoft Corporation" --depth quick
    python main.py --ticker AAPL --portfolio ./portfolio.json
"""

import argparse
import json
from pathlib import Path
import sys

from graph.workflow import run_analysis


def main():
    parser = argparse.ArgumentParser(
        description="MarketPulse — Autonomous Financial Intelligence Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ticker AAPL
  python main.py --ticker TSLA --depth deep
  python main.py --ticker MSFT --company "Microsoft Corporation"
    python main.py --ticker AAPL --portfolio ./portfolio.json
        """,
    )
    parser.add_argument("--ticker",  required=True,  help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--company", default="",     help="Full company name (auto-resolved if omitted)")
    parser.add_argument("--depth",   default="standard", choices=["quick","standard","deep"],
                        help="Analysis depth: quick (5d) | standard (1mo) | deep (3mo)")
    parser.add_argument("--portfolio", default="", help="Path to a JSON file of portfolio positions")

    args = parser.parse_args()

    portfolio_positions = []
    if args.portfolio:
        portfolio_path = Path(args.portfolio)
        if not portfolio_path.exists():
            raise FileNotFoundError(f"Portfolio file not found: {portfolio_path}")
        portfolio_positions = json.loads(portfolio_path.read_text(encoding="utf-8"))
        if not isinstance(portfolio_positions, list):
            raise ValueError("Portfolio JSON must be a list of position objects.")

    result = run_analysis(
        ticker=args.ticker,
        company_name=args.company,
        analysis_depth=args.depth,
        portfolio_positions=portfolio_positions,
    )

    print("\n" + "="*60)
    print("FINAL INVESTMENT REPORT")
    print("="*60)
    print(result.get("final_report", "No report generated."))

    if result.get("report_path"):
        print(f"\n📁 Report saved: {result['report_path']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
