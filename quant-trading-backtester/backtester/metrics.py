"""Performance and risk metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class MetricsResult:
    sharpe: float
    max_dd: float
    cagr: float
    win_rate: float
    profit_factor: float
    var_95: float
    cvar_95: float
    calmar: float
    sortino: float
    active_share: float


def _sharpe(returns: pd.Series, risk_free_rate: float) -> float:
    excess = returns - risk_free_rate / 252
    denom = excess.std(ddof=0)
    if denom == 0:
        return 0.0
    return excess.mean() / denom * np.sqrt(252)


def _max_drawdown(equity: pd.Series) -> float:
    drawdown = equity / equity.cummax() - 1.0
    return drawdown.min()


def _cagr(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years <= 0:
        return 0.0
    return (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1


def _win_rate(returns: pd.Series) -> float:
    non_zero = returns[returns != 0]
    if non_zero.empty:
        return 0.0
    return (non_zero > 0).mean()


def _profit_factor(returns: pd.Series) -> float:
    gains = returns[returns > 0].sum()
    losses = returns[returns < 0].sum()
    if losses == 0:
        return float("inf") if gains > 0 else 0.0
    return gains / abs(losses)


def _var_cvar(returns: pd.Series, level: float = 0.95) -> tuple[float, float]:
    if returns.empty:
        return 0.0, 0.0
    var = np.percentile(returns, (1 - level) * 100)
    cvar = returns[returns <= var].mean() if (returns <= var).any() else var
    return var, cvar


def _sortino(returns: pd.Series, risk_free_rate: float) -> float:
    downside = returns[returns < 0]
    if downside.std(ddof=0) == 0:
        return 0.0
    excess = returns - risk_free_rate / 252
    return excess.mean() / downside.std(ddof=0) * np.sqrt(252)


def _active_share(position: pd.Series, benchmark_weight: float = 1.0) -> float:
    if position.empty:
        return 0.0
    weights = position.abs().clip(0, 1)
    diff = (weights - benchmark_weight).abs()
    return 0.5 * diff.mean()


def compute_metrics(
    equity: pd.Series,
    returns: pd.Series,
    position: pd.Series,
    risk_free_rate: float,
) -> MetricsResult:
    sharpe = _sharpe(returns, risk_free_rate)
    max_dd = _max_drawdown(equity)
    cagr = _cagr(equity)
    win_rate = _win_rate(returns)
    profit_factor = _profit_factor(returns)
    var_95, cvar_95 = _var_cvar(returns, 0.95)
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0.0
    sortino = _sortino(returns, risk_free_rate)
    active_share = _active_share(position)

    return MetricsResult(
        sharpe=sharpe,
        max_dd=max_dd,
        cagr=cagr,
        win_rate=win_rate,
        profit_factor=profit_factor,
        var_95=var_95,
        cvar_95=cvar_95,
        calmar=calmar,
        sortino=sortino,
        active_share=active_share,
    )
