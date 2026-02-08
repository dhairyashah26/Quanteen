"""Vectorized backtesting engine."""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Tuple, Union

import numpy as np
import pandas as pd

from backtester.metrics import MetricsResult, compute_metrics
from backtester.portfolio import Portfolio
from config import DEFAULT_CONFIG
from data.fetcher import DataFetcher


class Backtester:
    def __init__(
        self,
        initial_capital: float = DEFAULT_CONFIG.initial_capital,
        commission: float = DEFAULT_CONFIG.commission,
        slippage: float = DEFAULT_CONFIG.slippage,
    ) -> None:
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self._strategies = []
        self._fetcher = DataFetcher()

    def add_strategy(self, strategy_instance) -> None:
        self._strategies.append(strategy_instance)

    def _combine_signals(self, signals: Iterable[pd.Series]) -> pd.Series:
        signal_list = list(signals)
        stacked = np.vstack(list(map(lambda s: s.fillna(0).to_numpy(), signal_list)))
        combined = stacked.mean(axis=0)
        return pd.Series(np.sign(combined), index=signal_list[0].index)

    def run(
        self,
        symbol: Union[str, Tuple[str, str]],
        timeframe: str,
        start_date: str,
        end_date: str,
    ) -> Dict[str, float]:
        if not self._strategies:
            raise ValueError("Add at least one strategy before running the backtest.")

        benchmark = self._fetcher.fetch("SPY", timeframe, start_date, end_date)
        benchmark_returns = benchmark["Close"].pct_change().fillna(0)

        if isinstance(symbol, tuple):
            data_a, data_b = tuple(map(lambda s: self._fetcher.fetch(s, timeframe, start_date, end_date), symbol))
            strategy = self._strategies[0]
            signal_data = strategy.generate_signals(data_a, data_b)
            spread_returns = signal_data["spread_return"]
            signals = signal_data["signal"]
            portfolio = Portfolio(
                self.initial_capital,
                self.commission,
                self.slippage,
                DEFAULT_CONFIG.risk_per_trade,
                DEFAULT_CONFIG.max_positions,
                DEFAULT_CONFIG.portfolio_stop_drawdown,
            )
            result = portfolio.simulate_spread(spread_returns, signals)
            metrics = compute_metrics(
                result.equity_curve,
                result.returns,
                result.positions,
                DEFAULT_CONFIG.risk_free_rate,
                benchmark_returns,
            )
            return metrics.__dict__

        data = self._fetcher.fetch(symbol, timeframe, start_date, end_date)
        signal_frames = list(map(lambda s: s.generate_signals(data), self._strategies))
        signals = self._combine_signals(list(map(lambda f: f["signal"], signal_frames)))
        atr = signal_frames[0]["atr"]
        portfolio = Portfolio(
            self.initial_capital,
            self.commission,
            self.slippage,
            DEFAULT_CONFIG.risk_per_trade,
            DEFAULT_CONFIG.max_positions,
            DEFAULT_CONFIG.portfolio_stop_drawdown,
        )
        result = portfolio.simulate(data["Close"], signals, atr)
        metrics = compute_metrics(
            result.equity_curve,
            result.returns,
            result.positions,
            DEFAULT_CONFIG.risk_free_rate,
            benchmark_returns.reindex(result.returns.index).fillna(0),
        )
        return metrics.__dict__
