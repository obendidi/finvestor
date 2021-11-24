import logging
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
import pytz
from httpx import AsyncClient, HTTPError
from pydantic import validate_arguments

from finvestor.core import YAHOO_FINANCE_HEADERS, config
from finvestor.data_providers.schemas import Bar, Bars
from finvestor.data_providers.utils import (
    DEFAULT_INTERVAL,
    DefaultString,
    ValidInterval,
    ValidPeriod,
    validate_start_end_period_args,
    time_period_to_timedelta,
)
from finvestor.data_providers.yahoo_finance.utils import (
    get_valid_intervals_for_datetime,
    get_valid_intervals_for_period,
    coerce_end_time_to_interval,
)

logger = logging.getLogger(__name__)


class UnprocessableEntity(HTTPError):
    pass


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_yahoo_finance_quotes(
    ticker: str,
    *,
    client: AsyncClient,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    period: Optional[ValidPeriod] = None,
    interval: ValidInterval = DEFAULT_INTERVAL,
):
    period, start, end = validate_start_end_period_args(
        period=period, start=start, end=end
    )
    params: Dict[str, Any] = {}

    if start is not None and end is not None:
        end = coerce_end_time_to_interval(interval, start, end)
        params["period1"] = int(datetime.timestamp(start))
        params["period2"] = int(datetime.timestamp(end))
    elif period is not None:
        params["range"] = period
    else:
        NotImplementedError()

    params["interval"] = interval
    params["includePrePost"] = True
    params["events"] = "div,splits"

    resp = await client.get(
        url=f"{config.YF_BASE_URL}/v8/finance/chart/{ticker}",
        params=params,
        headers=YAHOO_FINANCE_HEADERS,
    )
    if resp.status_code == 422:
        logger.error(f"Response with code 422 from Y-Finance [{ticker}]: {resp.json()}")
        raise UnprocessableEntity(resp.json())
    response = resp.json()
    error = response.get("chart", {}).get("error")
    if error:
        logger.error(f"Error response from Y-Finance [{ticker}]: {error}")
        raise UnprocessableEntity(error)

    result = response.get("chart", {}).get("result", [])
    if not len(result):
        raise UnprocessableEntity(f"Empty response: {response}")

    timestamps = result[0].get("timestamp")
    if not timestamps:
        raise UnprocessableEntity(f"Empty quotes: {response}")

    ohlc = result[0]["indicators"]["quote"][0]
    return timestamps, ohlc


async def get_yahoo_finance_bars(
    ticker: str,
    *,
    client: AsyncClient,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    period: Optional[ValidPeriod] = None,
    interval: ValidInterval = DEFAULT_INTERVAL,
) -> Bars:
    if period is not None and isinstance(interval, DefaultString):
        _valid_intervals = get_valid_intervals_for_period(interval, period)
    elif start is not None and isinstance(interval, DefaultString):
        _valid_intervals = get_valid_intervals_for_datetime(interval, start)
    else:
        _valid_intervals = [interval]

    if interval not in _valid_intervals:
        delta = (
            time_period_to_timedelta(period)
            if period is not None
            else pytz.utc.localize(datetime.utcnow()) - start  # type: ignore
        )
        logger.debug(
            f"YAHOO-FINANCE - '{ticker}' - '{interval}' data not availlable for "
            f"timedelta of '{delta.days} days', "
            f"supported intervals >= '{_valid_intervals[0]}'"
        )

    errors = []
    for _interval in _valid_intervals:
        try:
            if _interval != interval:
                logger.debug(
                    f"YAHOO-FINANCE - '{ticker}' - Trying with interval {_interval} ..."
                )
            timestamps, ohlc = await get_yahoo_finance_quotes(
                ticker,
                client=client,
                start=start,
                end=end,
                period=period,
                interval=_interval,
            )
            break
        except UnprocessableEntity as error:
            errors.append(error)
            continue
    else:
        raise UnprocessableEntity(str(errors))

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
