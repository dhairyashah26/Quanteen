"""CLI interface for the algorithmic trading backtester."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from typing import Dict

from backtester.engine import Backtester
from strategies import MeanReversionStrategy, MomentumStrategy, PairsTradingStrategy


def _ensure_dependencies() -> None:
    missing = [
        package
        for package in ("numpy", "pandas", "yfinance")
        if importlib.util.find_spec(package) is None
    ]
    if missing:
        missing_list = ", ".join(missing)
        message = (
            "Required dependencies are missing: "
            f"{missing_list}. This can happen in sandboxed environments that block "
            "outbound network access, which prevents `pip install -r requirements.txt` "
            "from downloading packages. Please run this project in a local Python "
            "environment or an unrestricted CI runner with internet access."
        )
        print(message, file=sys.stderr)
        sys.exit(1)


_ensure_dependencies()

import pandas as pd  # noqa: E402


def format_metrics(metrics: Dict[str, float]) -> str:
    lines = ["\nPerformance Metrics:"]
    for key, value in metrics.items():
        if isinstance(value, float):
            lines.append(f"- {key}: {value:.4f}")
        else:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def run_single(strategy_name: str, symbol: str, start: str, end: str, timeframe: str) -> None:
    backtester = Backtester()
    if strategy_name == "momentum":
        backtester.add_strategy(MomentumStrategy())
    elif strategy_name == "mean_reversion":
        backtester.add_strategy(MeanReversionStrategy())
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    metrics = backtester.run(symbol, timeframe, start, end)
    print(format_metrics(metrics))


def run_compare(symbol: str, start: str, end: str, timeframe: str) -> None:
    strategies = {
        "Momentum": MomentumStrategy(),
        "Mean Reversion": MeanReversionStrategy(),
    }
    results = {}
    for name, strategy in strategies.items():
        backtester = Backtester()
        backtester.add_strategy(strategy)
        results[name] = backtester.run(symbol, timeframe, start, end)
    df = pd.DataFrame(results).T
    print(df.round(4).to_string())


def run_pairs(start: str, end: str, timeframe: str) -> None:
    backtester = Backtester()
    backtester.add_strategy(PairsTradingStrategy())
    metrics = backtester.run(("GLD", "GC=F"), timeframe, start, end)
    print(format_metrics(metrics))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Production Algorithmic Trading Backtester")
    subparsers = parser.add_subparsers(dest="command", required=True)

    single_parser = subparsers.add_parser("momentum", help="Run momentum strategy")
    single_parser.add_argument("symbol")
    single_parser.add_argument("start")
    single_parser.add_argument("end")
    single_parser.add_argument("--timeframe", default="1d")

    mean_parser = subparsers.add_parser("mean_reversion", help="Run mean reversion strategy")
    mean_parser.add_argument("symbol")
    mean_parser.add_argument("start")
    mean_parser.add_argument("end")
    mean_parser.add_argument("--timeframe", default="1d")

    compare_parser = subparsers.add_parser("compare", help="Compare strategies")
    compare_parser.add_argument("symbol")
    compare_parser.add_argument("start")
    compare_parser.add_argument("end")
    compare_parser.add_argument("--timeframe", default="1d")

    pairs_parser = subparsers.add_parser("pairs", help="Run pairs trading strategy")
    pairs_parser.add_argument("start")
    pairs_parser.add_argument("end")
    pairs_parser.add_argument("--timeframe", default="1d")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "momentum":
        run_single("momentum", args.symbol, args.start, args.end, args.timeframe)
    elif args.command == "mean_reversion":
        run_single("mean_reversion", args.symbol, args.start, args.end, args.timeframe)
    elif args.command == "compare":
        run_compare(args.symbol, args.start, args.end, args.timeframe)
    elif args.command == "pairs":
        run_pairs(args.start, args.end, args.timeframe)
    else:
        raise ValueError("Unsupported command")


if __name__ == "__main__":
    main()
