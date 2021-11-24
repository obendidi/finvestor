from datetime import datetime
from typing import Optional
import logging

import pytz
from httpx import AsyncClient

from finvestor.core import config
from finvestor.data_providers.alpaca.bars import (
    get_alpaca_bars,
    is_before_apca_historical_delay,
)
from finvestor.data_providers.schemas import Bar, Bars
from finvestor.data_providers.utils import (
    DEFAULT_INTERVAL,
    ValidInterval,
    ValidPeriod,
    get_valid_period_for_interval,
    time_period_to_timedelta,
)
from finvestor.data_providers.yahoo_finance.bars import get_yahoo_finance_bars

logger = logging.getLogger(__name__)


async def get_bars(
    ticker: str,
    *,
    client: AsyncClient,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    period: Optional[ValidPeriod] = None,
    interval: ValidInterval = DEFAULT_INTERVAL,
) -> Bars:
    if config.DATA_PROVIDER == "alpaca":
        if end is not None and is_before_apca_historical_delay(end):
            bars = await get_alpaca_bars(
                ticker,
                client=client,
                start=start,
                end=end,
                period=period,
                interval=interval,
            )
            if bars is not None:
                return bars
            else:
                logger.debug(f"ALPACA - '{ticker}' - Falling back to YAHOO-FINANCE ...")
            # else we fall back to yahoo finance
        else:
            logger.debug(
                f"ALPACA - '{ticker}' - Provided end time '{end}' does not "
                "validate configured alpaca historical data delay "
                f"of {config.APCA_HISTORICAL_DATA_DELAY_SECONDS}."
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
    interval: ValidInterval = DEFAULT_INTERVAL,
) -> Bar:
    bars = await get_bars(
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
    interval: ValidInterval = DEFAULT_INTERVAL,
) -> Bar:

    assert timestamp.tzinfo == pytz.utc, (
        f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
        f"got: timestamp<{timestamp.tzinfo}>"
    )
    start = timestamp.replace(second=0)
    end = start + time_period_to_timedelta(interval) * 5
    bars = await get_bars(
        ticker, client=client, start=start, end=end, interval=interval
    )

    return bars[0]


async def get_price_at_timestamp(
    ticker: str,
    *,
    client: AsyncClient,
    timestamp: datetime,
) -> float:
    bar = await get_bar_at_timestamp(
        ticker, client=client, timestamp=timestamp, interval=DEFAULT_INTERVAL
    )
    bar_open_date = bar.timestamp
    bar_close_date = bar_open_date + time_period_to_timedelta(bar.interval)
    open_delta = timestamp - bar_open_date
    close_delta = bar_close_date - timestamp
    if open_delta < close_delta:
        return bar.open
    return bar.close
