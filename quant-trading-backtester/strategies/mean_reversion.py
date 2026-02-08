"""Mean reversion strategy using Bollinger Bands and RSI."""

from __future__ import annotations

import pandas as pd

from utils.indicators import atr, bollinger_bands, rsi


class MeanReversionStrategy:
    name = "Mean Reversion"

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        close = data["Close"]
        bands = bollinger_bands(close, 20, 2)
        rsi_val = rsi(close, 14)
        atr_val = atr(data["High"], data["Low"], close, 14)

        long_signal = (close < bands["lower"]) & (rsi_val < 30)
        short_signal = (close > bands["upper"]) | (rsi_val > 70)

        signal = pd.Series(0, index=close.index, dtype=float)
        signal = signal.mask(long_signal, 1.0)
        signal = signal.mask(short_signal, -1.0)

        position = []
        entry_price = None
        current = 0.0

        for idx, price in close.items():
            if current == 0 and signal.loc[idx] != 0:
                current = signal.loc[idx]
                entry_price = price
            elif current != 0 and entry_price is not None:
                stop_loss = entry_price - current * 3 * atr_val.loc[idx]
                if (current > 0 and price < stop_loss) or (current < 0 and price > stop_loss):
                    current = 0.0
                    entry_price = None
            if signal.loc[idx] == 0:
                position.append(current)
            else:
                position.append(signal.loc[idx])
                current = signal.loc[idx]
                entry_price = price

        position_series = pd.Series(position, index=close.index, dtype=float)
        return pd.DataFrame({"signal": position_series, "atr": atr_val})
