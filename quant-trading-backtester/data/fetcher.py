"""Market data fetcher using yfinance with smart caching."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf


@dataclass
class DataRequest:
    symbol: str
    timeframe: str
    start: str
    end: str


class DataFetcher:
    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        self.cache_dir = cache_dir or Path(__file__).resolve().parent.parent / "data_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, request: DataRequest) -> Path:
        safe_symbol = request.symbol.replace("=", "_").replace("-", "_")
        return self.cache_dir / f"{safe_symbol}_{request.timeframe}_{request.start}_{request.end}.csv"

    def fetch(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        request = DataRequest(symbol=symbol, timeframe=timeframe, start=start, end=end)
        cache_path = self._cache_path(request)
        if cache_path.exists():
            data = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            return self._clean(data, timeframe)

        try:
            data = yf.download(
                symbol,
                start=start,
                end=end,
                interval=timeframe,
                auto_adjust=True,
                progress=False,
            )
        except Exception as exc:  # pragma: no cover - yfinance errors are environment-specific
            raise RuntimeError(f"Failed to download data for {symbol}: {exc}") from exc

        if data.empty:
            raise ValueError(f"No data returned for {symbol}. The symbol may be delisted or invalid.")

        data = self._clean(data, timeframe)
        data.to_csv(cache_path)
        return data

    def _clean(self, data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        data = data.rename(columns=str.title)
        required = ["Open", "High", "Low", "Close", "Volume"]
        data = data[[col for col in required if col in data.columns]]
        data = data.sort_index()

        if timeframe in {"1d", "1h", "1m"}:
            return data

        rule = timeframe
        data = data.resample(rule).agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )
        data = data.dropna(how="all")
        return data
