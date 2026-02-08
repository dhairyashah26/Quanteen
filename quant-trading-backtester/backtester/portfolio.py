"""Portfolio construction and risk management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class PortfolioResult:
    equity_curve: pd.Series
    returns: pd.Series
    drawdown: pd.Series
    positions: pd.Series


class Portfolio:
    def __init__(
        self,
        initial_capital: float,
        commission: float,
        slippage: float,
        risk_per_trade: float,
        max_positions: int,
        portfolio_stop_drawdown: float,
    ) -> None:
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.portfolio_stop_drawdown = portfolio_stop_drawdown

    def simulate(
        self,
        close: pd.Series,
        signals: pd.Series,
        atr: pd.Series,
    ) -> PortfolioResult:
        price_change = close.diff().fillna(0)
        atr = atr.replace(0, np.nan).fillna(method="ffill").fillna(1.0)
        signals = signals.fillna(0).to_numpy()
        equity = np.zeros(len(close))
        positions = np.zeros(len(close))
        shares = np.zeros(len(close))
        equity[0] = self.initial_capital
        peak = self.initial_capital
        stopped = False

        for i in range(1, len(close)):
            if stopped:
                positions[i] = 0
                shares[i] = 0
            else:
                desired = signals[i - 1]
                if desired != positions[i - 1]:
                    risk_capital = equity[i - 1] * self.risk_per_trade
                    shares[i] = 0 if desired == 0 else risk_capital / atr.iloc[i - 1]
                    positions[i] = desired
                else:
                    positions[i] = positions[i - 1]
                    shares[i] = shares[i - 1]

            trade_value = abs(positions[i] * shares[i] - positions[i - 1] * shares[i - 1]) * close.iloc[i]
            costs = trade_value * (self.commission + self.slippage)
            pnl = positions[i - 1] * shares[i - 1] * price_change.iloc[i] - costs
            equity[i] = equity[i - 1] + pnl

            peak = max(peak, equity[i])
            if (equity[i] / peak - 1.0) <= -self.portfolio_stop_drawdown:
                stopped = True

        equity_series = pd.Series(equity, index=close.index)
        position_series = pd.Series(positions, index=close.index)
        drawdown = equity_series / equity_series.cummax() - 1.0
        returns = equity_series.pct_change().fillna(0)
        return PortfolioResult(equity_curve=equity_series, returns=returns, drawdown=drawdown, positions=position_series)

    def simulate_spread(
        self,
        spread_returns: pd.Series,
        signals: pd.Series,
    ) -> PortfolioResult:
        raw_equity = pd.Series(self.initial_capital, index=spread_returns.index, dtype=float)
        position = signals.shift(1).fillna(0)
        trade_value = position.diff().abs().fillna(0)
        costs = trade_value * (self.commission + self.slippage)
        pnl = position * spread_returns - costs
        equity = self.initial_capital + pnl.cumsum()
        drawdown = equity / equity.cummax() - 1.0
        breach = drawdown <= -self.portfolio_stop_drawdown
        if breach.any():
            stop_index = breach.idxmax()
            position = position.where(position.index < stop_index, 0)
            trade_value = position.diff().abs().fillna(0)
            costs = trade_value * (self.commission + self.slippage)
            pnl = position * spread_returns - costs
            equity = self.initial_capital + pnl.cumsum()
            drawdown = equity / equity.cummax() - 1.0
        returns = equity.pct_change().fillna(0)
        return PortfolioResult(equity_curve=equity, returns=returns, drawdown=drawdown, positions=position)
