import typing as tp
from datetime import datetime, timedelta

from pydantic import BaseModel

from finvestor.schemas.base import BaseDataFrameModel

__all__ = ("Bar", "Bars")


class Bar(BaseModel):
    timestamp: datetime
    close: float
    high: float
    low: float
    open: float
    volume: float
    interval: tp.Union[int, str, timedelta]


class Bars(BaseDataFrameModel):
    __root__: tp.List[Bar]
