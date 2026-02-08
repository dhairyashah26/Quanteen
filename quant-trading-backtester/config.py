"""Central configuration for the backtester."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestConfig:
    initial_capital: float = 100_000.0
    commission: float = 0.001
    slippage: float = 0.0005
    risk_per_trade: float = 0.02
    max_positions: int = 6
    portfolio_stop_drawdown: float = 0.20
    risk_free_rate: float = 0.02


DEFAULT_CONFIG = BacktestConfig()
