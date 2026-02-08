"""Pairs trading strategy using cointegration and z-score signals."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint

from utils.indicators import zscore


class PairsTradingStrategy:
    name = "Pairs Trading"

    def generate_signals(self, data_a: pd.DataFrame, data_b: pd.DataFrame) -> pd.DataFrame:
        close_a = data_a["Close"]
        close_b = data_b["Close"]
        aligned = pd.concat([close_a, close_b], axis=1, join="inner").dropna()
        close_a = aligned.iloc[:, 0]
        close_b = aligned.iloc[:, 1]

        beta = np.polyfit(close_b, close_a, 1)[0]
        spread = close_a - beta * close_b
        pvalue = coint(close_a, close_b)[1]

        if pvalue >= 0.05:
            signal = pd.Series(0.0, index=spread.index)
        else:
            z = zscore(spread, 20)
            signal = pd.Series(0.0, index=spread.index)
            current = 0.0
            for idx, value in z.items():
                if current == 0.0:
                    if value < -2.0:
                        current = 1.0
                    elif value > 2.0:
                        current = -1.0
                elif current != 0.0:
                    if (current > 0 and value >= 0) or (current < 0 and value <= 0):
                        current = 0.0
                signal.loc[idx] = current

        ret_a = close_a.pct_change().fillna(0)
        ret_b = close_b.pct_change().fillna(0)
        spread_return = ret_a - beta * ret_b
        return pd.DataFrame({"signal": signal, "spread_return": spread_return})
