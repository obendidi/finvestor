import typing as tp
from datetime import datetime, timedelta

from pydantic import BaseModel

from finvestor.schemas.base import BaseDataFrameModel

__all__ = ("Bar", "Bars")


class Bar(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    interval: tp.Union[int, str, timedelta]


class Bars(BaseDataFrameModel):
    __root__: tp.List[Bar]

    @property
    def df(self):
        if self._df is None:
            super().df
            self._df = self._df.set_index("timestamp")
        return self._df
