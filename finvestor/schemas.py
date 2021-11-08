from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel
from pydantic.fields import Field


class Asset(BaseModel):
    symbol: str
    currency: str = "USD"
    name: Optional[str]
    category: Optional[
        Literal["stock", "crypto", "ETF", "currency", "commodity", "cash"]
    ]
    industry: Optional[str]
    exchange: Optional[str]


class Transaction(BaseModel):
    asset: Asset
    type: Literal["BUY", "SELL", "DEPOSIT", "WITHDRAW"]
    open_date: datetime
    close_date: Optional[datetime]
    open_rate: float
    close_rate: Optional[float]
    units: float
    leverage: float = Field(default=1, ge=1)
    spread: float = 0
    fees: float = 0
    profit: Optional[float]
