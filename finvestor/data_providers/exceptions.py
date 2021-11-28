import typing as tp

from httpx import HTTPError

from finvestor import config


class EmptyBars(HTTPError):
    def __init__(self, ticker: str, resp: tp.Any) -> None:
        self.resp = resp
        self.ticker = ticker

    def __str__(self) -> str:
        assert config.DATA_PROVIDER is not None
        return (
            f"{config.DATA_PROVIDER.upper()} (ticker={self.ticker}) "
            f"responded with empty bars:  {self.resp}"
        )
