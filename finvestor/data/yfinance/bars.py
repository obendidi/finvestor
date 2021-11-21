import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pytz
from httpx import AsyncClient
from pydantic import validate_arguments

from finvestor.core import config
from finvestor.data.yfinance import YF_HEADERS
from finvestor.data.yfinance.exceptions import EmptyResponse, ErrorResponse
from finvestor.data.yfinance.utils import (
    ValidInterval,
    ValidRange,
    coerce_end_time_to_interval,
    get_valid_intervals_for_datetime,
    get_valid_intervals_for_range,
    time_symbol_to_timedelta,
)
from finvestor.models import Bar, Bars

logger = logging.getLogger(__name__)


async def get_quotes(
    ticker: str,
    *,
    client: AsyncClient,
    start: Optional[datetime],
    end: Optional[datetime],
    range: Optional[ValidRange],
    interval: ValidInterval = "1m",
    include_prepost: bool = False,
    coerce_interval: bool = False,
) -> Tuple[List[float], Dict]:

    params: Dict[str, Any] = {}

    if start is not None:
        assert start.tzinfo == pytz.utc, (
            f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
            f"got: start<{start.tzinfo}>"
        )
        if end is not None:
            assert end.tzinfo == pytz.utc, (
                f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
                f"got: end<{end.tzinfo}>"
            )
            assert end > start, (
                f"Provided end datetime ({end}) should be larger than start "
                f"datetime ({start})"
            )
            if coerce_interval:
                end = coerce_end_time_to_interval(ticker, interval, start, end)
        else:
            end = start + time_symbol_to_timedelta(interval)
        params["period1"] = int(datetime.timestamp(start))
        params["period2"] = int(datetime.timestamp(end))
    else:
        params["range"] = range

    params["interval"] = interval
    params["includePrePost"] = include_prepost
    params["events"] = "div,splits"
    resp = await client.get(
        url=f"{config.YF_BASE_URL}/v8/finance/chart/{ticker}",
        params=params,
        headers=YF_HEADERS,
    )
    response = resp.json()

    error = response.get("chart", {}).get("error")
    if error:
        logger.error(f"Error response from Y-Finance [{ticker}]: {error}")
        raise ErrorResponse(error)

    result = response.get("chart", {}).get("result", [])
    if not len(result):
        logger.error(
            f"Empty response from Y-Finance [{ticker}]: range={range} | "
            f"interval={interval} | start={start} | end={end}"
        )
        raise EmptyResponse(f"Empty response: {response}")

    timestamps = result[0].get("timestamp")
    if not timestamps:
        logger.error(
            f"Empty quotes from Y-Finance [{ticker}]: range={range} | "
            f"interval={interval} | start={start} | end={end}"
        )
        raise EmptyResponse(f"Empty quotes: {response}")

    ohlc = result[0]["indicators"]["quote"][0]
    return timestamps, ohlc


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_bars(
    ticker: str,
    *,
    client: AsyncClient,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    range: Optional[ValidRange] = None,
    interval: ValidInterval = "1m",
    include_prepost: bool = False,
    coerce_interval: bool = True,
) -> Bars:

    assert (
        range is not None or start is not None
    ), "please provide either a range or start[-end] datetimes"

    if range is not None and coerce_interval:
        _valid_intervals = get_valid_intervals_for_range(interval, range)
    elif start is not None and coerce_interval:
        _valid_intervals = get_valid_intervals_for_datetime(interval, start)
    else:
        _valid_intervals = [interval]

    if interval not in _valid_intervals:
        logger.debug(
            f"[{ticker}]: {interval} interval is not supported by yahoo-finance "
            f"for provided range ({range}), or start/end datetimes ({start}/{end}). "
            f"Supported intervals for your request: {_valid_intervals}"
        )
    errors = []
    for _interval in _valid_intervals:
        try:
            timestamps, ohlc = await get_quotes(
                ticker,
                client=client,
                start=start,
                end=end,
                range=range,
                interval=_interval,
                include_prepost=include_prepost,
                coerce_interval=coerce_interval,
            )
            break
        except EmptyResponse as error:
            errors.append(error)
            continue
    else:
        raise EmptyResponse(errors)
    bars = Bars(
        __root__=[
            Bar(
                timestamp=timestamp,
                close=close if close is not None else np.nan,
                high=high if high is not None else np.nan,
                low=low if low is not None else np.nan,
                open=open if open is not None else np.nan,
                volume=volume if volume is not None else np.nan,
                interval=_interval,
            )
            for timestamp, volume, open, close, low, high in zip(
                timestamps,
                ohlc["volume"],
                ohlc["open"],
                ohlc["close"],
                ohlc["low"],
                ohlc["high"],
            )
        ]
    )
    return bars


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_latest_bar(
    ticker: str,
    *,
    client: AsyncClient,
    interval: ValidInterval = "1m",
    include_prepost: bool = True,
) -> Bar:

    if interval.endswith("m") or interval.endswith("h"):
        range = "1d"
    elif interval.endswith("d"):
        range = "1mo"
    else:
        range = "6mo"
    bars = await get_bars(
        ticker,
        client=client,
        include_prepost=include_prepost,
        range=range,  # type: ignore
    )
    return bars[-1]


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_bar_at_timestamp(
    ticker: str,
    *,
    client: AsyncClient,
    timestamp: datetime,
) -> Bar:
    assert timestamp.tzinfo == pytz.utc, (
        f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
        f"got: timestamp<{timestamp.tzinfo}>"
    )
    interval: ValidInterval = "1m"
    start = timestamp.replace(second=0)

    bars = await get_bars(ticker, client=client, start=start, interval=interval)
    return bars[0]


async def get_closest_price_at_timestamp(
    ticker: str,
    *,
    client: AsyncClient,
    timestamp: datetime,
) -> float:
    bar = await get_bar_at_timestamp(ticker, client=client, timestamp=timestamp)
    bar_open_date = bar.timestamp
    bar_close_date = bar_open_date + time_symbol_to_timedelta(bar.interval)
    open_delta = timestamp - bar_open_date
    close_delta = bar_close_date - timestamp
    if open_delta < close_delta:
        return bar.open
    return bar.close


if __name__ == "__main__":
    from finvestor.core import setup_logging
    from finvestor.etoro.utils import parse_etoro_datetime

    setup_logging()

    async def main():
        ticker = "FB"
        async with AsyncClient() as client:
            date = parse_etoro_datetime("28/09/2021 15:13:03")
            bars = await get_bar_at_timestamp(ticker, client=client, timestamp=date)
            print(bars)

    asyncio.run(main())
