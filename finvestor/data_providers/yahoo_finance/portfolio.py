import asyncio
import io
import typing as tp

import pandas as pd
from anyio import open_file
from httpx import AsyncClient
from rich.progress import track

from finvestor.data_providers.yahoo_finance import get_asset
from finvestor.schemas.asset import Asset
from finvestor.schemas.transaction import Transactions

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
    "Symbol": "ticker",
    "Trade Date": "open_date",
    "Purchase Price": "open_rate",
    "Quantity": "quantity",
    "Commission": "commission",
}


async def load_yf_csv_quotes(filepath: str, *, client: AsyncClient) -> Transactions:
    async with await open_file(filepath, "rb") as file:
        contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    # drop unecessary columns
    df = df.drop(columns=YF_CSV_QUOTES_DROP_COLS)
    # remove rows that have a symbol that starts with $$
    # $$ is for custom symbols in TF, to do exampe add cash or other stuff
    df = df[~df["Symbol"].str.startswith("$$", na=False)]
    # rename columns to what we use internally
    df = df.rename(columns=YF_CSV_QUOTES_RENAME_COLS)
    # convert open_date to datetime.
    df["open_date"] = pd.to_datetime(df["open_date"], utc=True, format="%Y%m%d")
    # load asset information from yahoo finance
    assets = await load_assets(df.ticker.unique(), client=client)
    # map an asset for each ticker
    df["asset"] = df["ticker"].map({asset.ticker: asset for asset in assets})
    return Transactions(__root__=df.to_dict(orient="records"))


async def load_assets(tickers: tp.List[str], *, client: AsyncClient) -> tp.List[Asset]:
    tasks = [get_asset(ticker, client=client) for ticker in tickers]
    return [
        await task
        for task in track(
            asyncio.as_completed(tasks),
            description=f"[green]Loading {len(tasks)} Assets info from yahoo-finance",
            total=len(tasks),
        )
    ]
