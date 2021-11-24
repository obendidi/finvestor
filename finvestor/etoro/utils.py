import asyncio
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import pytz
from httpx import AsyncClient

from finvestor.data_providers import get_asset, get_price_at_timestamp

logger = logging.getLogger(__name__)

ETORO_DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"


def parse_etoro_datetime(etoro_datetime: str) -> datetime:
    """Parse an etoro datetime, to python datetime object with UTC timezone.

    Args:
        etoro_datetime: Etoro datetime string.

    Returns:
        datetime: dateime object with utc timezone
    """
    date = datetime.strptime(etoro_datetime, ETORO_DATETIME_FORMAT)
    return pytz.utc.localize(date)


async def fill_nan_ticker(
    df: pd.DataFrame, ticker: str, *, client: AsyncClient
) -> None:
    # get valid name index if exists
    valid_name_idx = df.loc[df.ticker == ticker, "name"].first_valid_index()
    # if a name already exists
    if valid_name_idx is not None:
        name, isin = df.loc[valid_name_idx, ["name", "ISIN"]]
    else:
        asset = await get_asset(ticker, client=client)
        name = asset.name
        isin = asset.isin or np.nan

    df.loc[df.ticker == ticker, ["name", "ISIN"]] = name, isin

    # get open_rate for non closed positions
    if df.loc[df.ticker == ticker, "open_rate"].isnull().values.any():
        _df_to_fill = df.loc[
            (df.ticker == ticker) & (df.open_rate.isna()), ["open_date", "invested"]
        ]
        open_rates = await asyncio.gather(
            *[
                get_price_at_timestamp(ticker, client=client, timestamp=open_date)
                for open_date in _df_to_fill.open_date
            ]
        )
        units = _df_to_fill.invested / open_rates
        _fill_data = [(open_rate, unit) for open_rate, unit in zip(open_rates, units)]
        df.loc[
            (df.ticker == ticker) & (df.open_rate.isna()), ["open_rate", "units"]
        ] = _fill_data
