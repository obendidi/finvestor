import logging
import typing as tp
from collections.abc import Sequence
from datetime import datetime

import pandas as pd
import pytz
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

ValidInterval = tp.Literal[
    "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"
]
AutoValidInterval = tp.Union[tp.Literal["auto"], ValidInterval]
ValidPeriod = tp.Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd"
]

VALID_INTERVALS: tp.Tuple[ValidInterval, ...] = tp.get_args(ValidInterval)


class Asset(BaseModel):
    ticker: str
    name: str
    type: str
    currency: str
    exchange: str
    exchange_timezone: str
    market: str
    isin: tp.Optional[str]
    country: tp.Optional[str]
    sector: tp.Optional[str]
    industry: tp.Optional[str]


class Bar(BaseModel):
    timestamp: datetime
    close: float
    high: float
    low: float
    open: float
    volume: float
    interval: ValidInterval


class Bars(BaseModel, Sequence):
    __root__: tp.List[Bar] = Field(..., min_items=1)

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


class BaseBarsRequestParams(BaseModel):
    start: tp.Optional[datetime]
    end: tp.Optional[datetime]
    period: tp.Optional[ValidPeriod]
    interval: AutoValidInterval = "auto"

    @validator("period")
    def check_duplicate(cls, period: ValidPeriod, values) -> ValidPeriod:
        start = values.get("start")
        if start is None and period is None:
            raise ValueError("Missing values: 'period' or 'start'.")
        if start is not None and period is not None:
            raise ValueError("Duplicate values: 'period' and 'start'.")
        return period

    @validator("end")
    def check_invalid_end_value(
        cls, end: tp.Optional[datetime], values
    ) -> tp.Optional[datetime]:
        start = values.get("start")
        if end is not None and start is None:
            raise ValueError("Missing value: 'start'.")
        if start is not None and end is not None and end < start:
            raise ValueError("Invalid value: 'end' < 'start'.")
        return end

    @validator("start", "end")
    def check_tz_utc(cls, value: tp.Optional[datetime]) -> tp.Optional[datetime]:
        if value is None:
            return value
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError(f"Missing timezone info: {value}")
        if value.tzinfo == pytz.UTC:
            return value
        return value.astimezone(pytz.UTC)

    def params(self, **kwargs: tp.Any) -> tp.Dict[str, tp.Any]:
        data = self.dict(exclude_none=True)
        data.update(kwargs)
        return data
