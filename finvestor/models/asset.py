from typing import Optional

from pydantic import BaseModel


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
