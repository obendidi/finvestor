from collections.abc import Sequence
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import pytz

import pandas as pd
from pydantic import BaseModel, Field, validator

from finvestor.data_providers.utils import pytz_utc_now
from finvestor.data_providers.timeframe import TimeFrame

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


class GetBarsDataParms(BaseModel):
    interval: TimeFrame = TimeFrame("1m")
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    period: Optional[TimeFrame] = None

    @validator("period")
    def check_period_or_start(
        cls, period: TimeFrame[str], values: Dict[str, Any]
    ) -> TimeFrame[str]:
        start = values.get("start")
        end = values.get("end")
        if start is None and period is None:
            raise ValueError("Please provide either a period or start[-end] datetimes.")
        if (start is not None or end is not None) and period is not None:
            raise ValueError(
                "Please provide ONLY one of period or start[-end] datetimes."
            )
        return period

    @validator("start", "end")
    def check_tz_is_utc(cls, _dt: datetime) -> datetime:
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
    def check_start_is_smaller_than_now(cls, start: datetime) -> datetime:
        if start is not None:
            now = pytz_utc_now()
            if start >= now:
                raise ValueError(
                    f"Provided start is invalid: start<{start}> >= now<{now}>."
                )
        return start

    @validator("end")
    def check_end_is_larger_than_start(
        cls, end: datetime, values: Dict[str, Any]
    ) -> datetime:
        start = values.get("start")
        if end is not None and start is not None:
            if start >= end:
                raise ValueError(
                    f"Provided end is invalid: start<{start}> >= end<{end}>."
                )
        return end
