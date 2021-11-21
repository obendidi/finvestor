from collections.abc import Sequence
from datetime import datetime
from typing import List, Literal

import pandas as pd
from pydantic import BaseModel, Field

ValidInterval = Literal["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"]


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


if __name__ == "__main__":
    bar1 = Bar(
        timestamp=datetime(2001, 12, 14),
        close=0.0,
        high=15,
        low=4,
        open=52,
        volume=44557,
    )
    bar2 = Bar(
        timestamp=datetime(2012, 12, 14),
        close=33.25,
        high=999,
        low=589,
        open=636,
        volume=1,
    )
    bars = Bars(__root__=[bar1, bar2])
    print(bars[-1])
