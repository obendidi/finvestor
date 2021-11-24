from collections.abc import Sequence
from datetime import datetime
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, Field

from finvestor.data_providers.utils import ValidInterval


class Asset(BaseModel):
    ticker: str
    name: str
    type: str
    currency: str
    exchange: str
    exchange_timezone: str
    market: str
    isin: Optional[str]
    country: Optional[str]
    sector: Optional[str]
    industry: Optional[str]


class Bar(BaseModel):
    timestamp: datetime
    close: float
    high: float
    low: float
    open: float
    volume: float
    interval: ValidInterval


class Bars(BaseModel, Sequence):
    __root__: List[Bar] = Field(..., min_items=1)

    def __getitem__(self, i):
        return self.__dict__.get("__root__")[i]

    def __len__(self):
        return len(self.__dict__.get("__root__"))

    def df(self) -> pd.DataFrame:
        bars_df = pd.DataFrame(self.dict().get("__root__"))
        bars_df["timestamp"] = pd.to_datetime(bars_df["timestamp"])
        bars_df = bars_df.set_index("timestamp")
        bars_df = bars_df.dropna(
            subset=["close", "open", "high", "low", "volume"], how="all"
        )
        return bars_df
