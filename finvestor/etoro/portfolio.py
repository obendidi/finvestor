import asyncio
import logging
from datetime import datetime
from typing import List

import attr
import pandas as pd
from anyio import open_file
from httpx import AsyncClient
from tqdm import tqdm

from finvestor.etoro.parsers import parse_etoro_account_statement
from finvestor.etoro.schemas import EtoroAccountStatement
from finvestor.etoro.utils import fill_nan_ticker

logger = logging.getLogger(__name__)


@attr.s
class EtoroPortfolio:

    statement: EtoroAccountStatement = attr.ib(kw_only=True)
    _client: AsyncClient = attr.ib(kw_only=True)

    @classmethod
    async def load(cls, filepath: str, *, client: AsyncClient) -> "EtoroPortfolio":
        async with await open_file(filepath, "rb") as file:
            contents = await file.read()
        sheets = pd.read_excel(contents, sheet_name=None)
        portfolio = cls(statement=parse_etoro_account_statement(sheets), client=client)
        await portfolio.fill_missing()
        return portfolio

    @property
    def username(self) -> str:
        return self.statement.account_summary.username

    @property
    def currency(self) -> str:
        return self.statement.account_summary.currency

    @property
    def start_date(self) -> datetime:
        return self.statement.account_summary.start_date

    @property
    def end_date(self) -> datetime:
        return self.statement.account_summary.end_date

    @property
    def transactions(self) -> pd.DataFrame:
        return self.statement.transactions

    @property
    def cash(self) -> float:
        return self.transactions.iloc[-1]["balance_open"]

    @property
    def tickers(self) -> List[str]:
        return list(self.transactions["ticker"].unique())

    @property
    def open_positions(self) -> pd.DataFrame:
        return self.transactions.loc[self.transactions.close_rate.isna()]

    async def fill_missing(self) -> None:
        pbar = tqdm(desc="Filling missing data", unit="ticker", total=len(self.tickers))
        await asyncio.gather(
            *[
                fill_nan_ticker(
                    self.transactions, ticker, client=self._client, pbar=pbar
                )
                for ticker in self.tickers
            ]
        )

    def export_yf(self, export_path: str) -> None:
        df = self.open_positions[["ticker", "open_date", "open_rate", "units"]]
        df.open_date = df.open_date.dt.strftime("%Y%m%d")
        df = df.rename(
            columns={
                "ticker": "Symbol",
                "open_date": "Trade Date",
                "open_rate": "Purchase Price",
                "units": "Quantity",
            }
        )
        cash_row = {
            "Symbol": "$$CASH",
            "Trade Date": self.end_date.strftime("%Y%m%d"),
            "Purchase Price": 1,
            "Quantity": self.cash,
        }
        df = df.append(cash_row, ignore_index=True)  # type: ignore
        df.to_csv(export_path, index=False, header=True)


if __name__ == "__main__":
    from finvestor.core import setup_logging

    setup_logging()

    async def main():
        filepath = "data/etoro-account-statement-12-1-2019-10-24-2021.xlsx"
        async with AsyncClient() as client:
            portfolio = await EtoroPortfolio.load(filepath, client=client)

        portfolio.export_yf("quotes.csv")

    asyncio.run(main())
