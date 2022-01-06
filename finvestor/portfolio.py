import asyncio
from datetime import datetime

from httpx import AsyncClient

from finvestor.schemas.transaction import Transactions
from finvestor.yahoo_finance import load_yf_csv_quotes


class Portfolio:
    def __init__(
        self, transactions: Transactions, *, name: str, start_date: datetime
    ) -> None:
        self.transactions = transactions
        self.name = name
        self.start_date = start_date

    @classmethod
    async def from_yahoo_finance_csv(
        cls, filepath: str, *, client: AsyncClient
    ) -> "Portfolio":

        transactions = await load_yf_csv_quotes(filepath, client=client)
        start_date = min(transactions.df["open_date"])
        name = f"yahoo-finance-{start_date}"
        return cls(transactions, name=name, start_date=start_date)


if __name__ == "__main__":

    async def main():
        async with AsyncClient() as client:
            transactions = await Portfolio.from_yahoo_finance_csv(
                "data/quotes.csv", client=client
            )
        print(transactions.df)

    asyncio.run(main())
