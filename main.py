"""
MarketPulse CLI Entry Point
Run a full analysis from the command line.

Usage:
    python main.py --ticker AAPL
    python main.py --ticker TSLA --depth deep
    python main.py --ticker MSFT --company "Microsoft Corporation" --depth quick
"""

import argparse
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
        """,
    )
    parser.add_argument("--ticker",  required=True,  help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--company", default="",     help="Full company name (auto-resolved if omitted)")
    parser.add_argument("--depth",   default="standard", choices=["quick","standard","deep"],
                        help="Analysis depth: quick (5d) | standard (1mo) | deep (3mo)")

    args = parser.parse_args()

    result = run_analysis(
        ticker=args.ticker,
        company_name=args.company,
        analysis_depth=args.depth,
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
