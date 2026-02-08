import numpy as np
import pandas as pd

from backtester.metrics import compute_metrics
from backtester.portfolio import Portfolio
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy


def sample_data() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=120, freq="D")
    price = pd.Series(np.linspace(100, 130, len(dates)), index=dates)
    high = price * 1.01
    low = price * 0.99
    volume = pd.Series(1_000_000, index=dates)
    return pd.DataFrame({"Open": price, "High": high, "Low": low, "Close": price, "Volume": volume})


def test_momentum_signals():
    data = sample_data()
    strategy = MomentumStrategy()
    signals = strategy.generate_signals(data)
    assert "signal" in signals.columns
    assert "atr" in signals.columns


def test_mean_reversion_signals():
    data = sample_data()
    strategy = MeanReversionStrategy()
    signals = strategy.generate_signals(data)
    assert signals["signal"].notna().all()


def test_portfolio_metrics():
    data = sample_data()
    strategy = MomentumStrategy()
    signals = strategy.generate_signals(data)
    portfolio = Portfolio(100_000, 0.001, 0.0005, 0.02, 6, 0.2)
    result = portfolio.simulate(data["Close"], signals["signal"], signals["atr"])
    benchmark = pd.Series(0.0, index=result.returns.index)
    metrics = compute_metrics(result.equity_curve, result.returns, result.positions, 0.02, benchmark)
    assert metrics.sharpe == metrics.sharpe
    assert metrics.max_dd <= 0
