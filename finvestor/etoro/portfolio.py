from typing import List

import attr
import pandas as pd

from finvestor.alpaca import AlpacaClient


@attr.s
class EtoroPortfolio:
    transactions: pd.DataFrame = attr.ib(kw_only=True)
    alpaca_client = AlpacaClient()

    @property
    def cash(self) -> float:
        return self.transactions.iloc[-1]["balance_open"]

    @property
    def tickers(self) -> List[str]:
        return list(self.transactions["ticker"].unique())
