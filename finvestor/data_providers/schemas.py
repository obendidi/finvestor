import logging
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import pytz
from pydantic import BaseModel, Field, validator

from finvestor.data_providers.timeframe import TimeFrame
from finvestor.data_providers.utils import pytz_utc_now

logger = logging.getLogger(__name__)


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
    interval: TimeFrame[str]


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


class GetBarsDataParams(BaseModel):
    interval: TimeFrame = TimeFrame(timedelta(minutes=1))
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    period: Optional[TimeFrame] = None

    @validator("period", always=True)
    def check_valid_start_or_valid_period_for_interval(
        cls, period: Optional[TimeFrame], values
    ) -> Optional[TimeFrame]:
        start = values.get("start")
        end = values.get("end")
        interval: TimeFrame = values.get("interval")
        if start is None and period is None:
            raise ValueError("Please provide either a period or start[-end] datetimes.")
        if (start is not None or end is not None) and period is not None:
            raise ValueError(
                "Please provide ONLY one of period or start[-end] datetimes."
            )

        if period is not None and interval >= period:
            raise ValueError(
                f"Interval={interval} is larger than provided period={period}"
            )

        if start is not None and end is not None:
            diff: TimeFrame[timedelta] = TimeFrame(end - start)
            if diff < interval:
                raise ValueError(
                    f"Interval={interval} is larger than diff between start-end, "
                    f"diff={diff}"
                )

        return period

    @validator("start", "end")
    def check_tz_is_utc(cls, _dt: Optional[datetime]) -> Optional[datetime]:
        if _dt is not None:
            if _dt.tzinfo is None or _dt.tzinfo.utcoffset(_dt) is None:
                raise ValueError(
                    f"Please provide an UTC start[-end] datetimes (or tz aware), "
                    f"got: {_dt}"
                )
            if _dt.tzinfo == pytz.utc:
                return _dt
            return _dt.astimezone(pytz.UTC)
        return _dt

    @validator("start")
    def check_start_is_smaller_than_now(
        cls, start: Optional[datetime]
    ) -> Optional[datetime]:
        if start is not None:
            now = pytz_utc_now()
            if start >= now:
                raise ValueError(
                    f"Provided start is invalid: start<{start}> >= now<{now}>."
                )
        return start

    @validator("end")
    def check_end_is_larger_than_start(
        cls, end: Optional[datetime], values
    ) -> Optional[datetime]:
        start = values.get("start")
        if end is not None and start is not None:
            if start >= end:
                raise ValueError(
                    f"Provided end is invalid: start<{start}> >= end<{end}>."
                )
        return end
