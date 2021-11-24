from datetime import datetime
from typing import Optional, Tuple

import pytz
from httpx import AsyncClient
from pydantic import validate_arguments

from finvestor.core import config
from finvestor.data_providers.alpaca.bars import (
    get_alpaca_bars,
    is_before_apca_hstorical_delay,
)
from finvestor.data_providers.schemas import Bar, Bars
from finvestor.data_providers.utils import (
    ValidInterval,
    ValidPeriod,
    get_valid_period_for_interval,
    time_period_to_timedelta,
)
from finvestor.data_providers.yahoo_finance.bars import get_yahoo_finance_bars


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_bars(
    ticker: str,
    *,
    client: AsyncClient,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    period: Optional[ValidPeriod] = None,
    interval: ValidInterval = "1m",
) -> Bars:
    if config.DATA_PROVIDER == "alpaca":
        return await get_alpaca_bars(
            ticker,
            client=client,
            start=start,
            end=end,
            period=period,
            interval=interval,
        )
    return await get_yahoo_finance_bars(
        ticker,
        client=client,
        start=start,
        end=end,
        period=period,
        interval=interval,
    )


async def get_latest_bar(
    ticker: str,
    *,
    client: AsyncClient,
    interval: ValidInterval = "1m",
) -> Bar:
    if (
        config.DATA_PROVIDER == "alpaca"
        and config.APCA_HISTORICAL_DATA_DELAY_SECONDS.total_seconds() == 0
    ):
        bars = await get_alpaca_bars(
            ticker,
            client=client,
            interval=interval,
            period=get_valid_period_for_interval(interval),
        )
    else:
        bars = await get_yahoo_finance_bars(
            ticker,
            client=client,
            interval=interval,
            period=get_valid_period_for_interval(interval),
        )
    return bars[-1]


async def get_bar_at_timestamp(
    ticker: str,
    *,
    client: AsyncClient,
    timestamp: datetime,
    interval: ValidInterval = "1m",
) -> Bar:
    assert timestamp.tzinfo == pytz.utc, (
        f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
        f"got: timestamp<{timestamp.tzinfo}>"
    )
    start = timestamp.replace(second=0)
    end = start + time_period_to_timedelta(interval)
    if is_before_apca_hstorical_delay(end):
        bars = await get_bars(
            ticker, client=client, start=start, end=end, interval=interval
        )
    else:
        bars = await get_yahoo_finance_bars(
            ticker, client=client, start=start, end=end, interval=interval
        )
    return bars[0]


async def get_price_at_timestamp(
    ticker: str,
    *,
    client: AsyncClient,
    timestamp: datetime,
) -> Tuple[datetime, float]:
    bar = await get_bar_at_timestamp(
        ticker, client=client, timestamp=timestamp, interval="1m"
    )
    bar_open_date = bar.timestamp
    bar_close_date = bar_open_date + time_period_to_timedelta(bar.interval)
    open_delta = timestamp - bar_open_date
    close_delta = bar_close_date - timestamp
    if open_delta < close_delta:
        return bar_open_date, bar.open
    return bar_close_date, bar.close
