import typing as tp
from datetime import datetime, timezone

from pydantic import BaseModel, validator
from pydantic.fields import Field, ModelField

from finvestor.schemas.asset import Asset
from finvestor.schemas.base import BaseDataFrameModel


class Transaction(BaseModel):
    asset: Asset
    type: tp.Literal["BUY", "SELL"] = "BUY"
    quantity: float = Field(gt=0)
    open_date: datetime
    open_rate: float
    currency: str = "USD"
    commission: float = 0.0

    @validator("open_date")
    def check_tz_utc(cls, value: datetime, field: ModelField) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError(f"Missing {field} timezone info: {value}")
        if value.tzinfo == timezone.utc:
            return value
        return value.astimezone(timezone.utc)


class Transactions(BaseDataFrameModel):
    __root__: tp.List[Transaction]
