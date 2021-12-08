import asyncio
import io

import pandas as pd
from anyio import open_file
from httpx import AsyncClient
from rich.progress import track

from finvestor.yahoo_finance.api.scrapper import get_asset

YF_CSV_QUOTES_DROP_COLS = [
    "Current Price",
    "Date",
    "Time",
    "Change",
    "Open",
    "High",
    "Low",
    "Volume",
    "High Limit",
    "Low Limit",
    "Comment",
]
YF_CSV_QUOTES_RENAME_COLS = {
    "Symbol": "asset",
    "Trade Date": "open_date",
    "Purchase Price": "open_rate",
    "Quantity": "units",
    "Commission": "commission",
}


async def parse_yf_csv_quotes(filepath: str, *, client: AsyncClient) -> pd.DataFrame:
    async with await open_file(filepath, "rb") as file:
        contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    df = df.drop(columns=YF_CSV_QUOTES_DROP_COLS)
    df = df[~df["Symbol"].str.startswith("$$", na=False)]

    tasks = [get_asset(ticker, client=client) for ticker in df["Symbol"].unique()]
    assets = [
        await task
        for task in track(
            asyncio.as_completed(tasks),
            description="[green]Loading Assets metadata:",
            total=len(tasks),
        )
    ]

    df["Symbol"] = df["Symbol"].map({asset.ticker: asset for asset in assets})

    df = df.rename(columns=YF_CSV_QUOTES_RENAME_COLS)
    df["amount"] = df.units * df.open_rate
    df["open_date"] = pd.to_datetime(df["open_date"], utc=True, format="%Y%m%d")
    return df


if __name__ == "__main__":

    async def main():
        async with AsyncClient() as client:
            await parse_yf_csv_quotes("data/quotes.csv", client=client)

    asyncio.run(main())
