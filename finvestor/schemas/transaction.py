import typing as tp
from datetime import datetime

import pytz
from pydantic import BaseModel, validator
from pydantic.fields import ModelField

from finvestor.schemas.base import BaseDataFrameModel

__all__ = ("Transaction", "Transactions")


class Transaction(BaseModel):
    ticker: str
    units: float
    open_date: datetime
    open_rate: float
    amount: float
    currency: str = "USD"
    close_date: tp.Optional[datetime]
    close_rate: tp.Optional[float]
    commission: tp.Optional[float]

    @validator("open_date", "close_date")
    def check_tz_utc(cls, value: datetime, field: ModelField) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError(f"Missing {field} timezone info: {value}")
        if value.tzinfo == pytz.UTC:
            return value
        return value.astimezone(pytz.UTC)

    @validator("amount")
    def check_amount_is_units_x_open_rate(cls, amount: float, values) -> float:
        computed_amount = values["open_rate"] * values["units"]
        if amount != computed_amount:
            raise ValueError(
                f"Invalid amount: expected={amount}, recieved={computed_amount}"
            )
        return amount


class Transactions(BaseDataFrameModel):
    __root__: tp.List[Transaction]
