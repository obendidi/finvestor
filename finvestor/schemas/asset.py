import typing as tp

from pydantic import BaseModel


class Asset(BaseModel):
    ticker: str
    name: tp.Optional[str]
    type: tp.Optional[str]
    currency: tp.Optional[str]
    exchange: tp.Optional[str]
    exchange_timezone: tp.Optional[str]
    market: tp.Optional[str]
    isin: tp.Optional[str]
    country: tp.Optional[str]
    sector: tp.Optional[str]
    industry: tp.Optional[str]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.ticker})"

    def __str__(self):
        return repr(self)
