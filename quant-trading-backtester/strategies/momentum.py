"""Momentum strategy with SMA crossover and RSI filter."""

from __future__ import annotations

import pandas as pd

from utils.indicators import atr, rsi, sma


class MomentumStrategy:
    name = "Momentum"

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        close = data["Close"]
        sma_fast = sma(close, 10)
        sma_slow = sma(close, 50)
        rsi_val = rsi(close, 14)
        atr_val = atr(data["High"], data["Low"], close, 20)

        long_signal = (sma_fast > sma_slow) & (rsi_val < 70)
        short_signal = (sma_fast < sma_slow) | (rsi_val > 80)

        signal = pd.Series(0, index=close.index, dtype=float)
        signal = signal.mask(long_signal, 1.0)
        signal = signal.mask(short_signal, -1.0)

        return pd.DataFrame({"signal": signal, "atr": atr_val})
