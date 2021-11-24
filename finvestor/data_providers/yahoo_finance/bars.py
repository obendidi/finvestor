import logging
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
from httpx import AsyncClient, HTTPError
from pydantic import validate_arguments

from finvestor.core import YAHOO_FINANCE_HEADERS, config
from finvestor.data_providers.schemas import Bar, Bars
from finvestor.data_providers.utils import (
    ValidInterval,
    ValidPeriod,
    validate_start_end_period_args,
)

logger = logging.getLogger(__name__)


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_yahoo_finance_bars(
    ticker: str,
    *,
    client: AsyncClient,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    period: Optional[ValidPeriod] = None,
    interval: ValidInterval = "1m",
) -> Bars:

    period, start, end = validate_start_end_period_args(
        period=period, start=start, end=end
    )

    params: Dict[str, Any] = {}

    if start is not None and end is not None:
        params["period1"] = int(datetime.timestamp(start))
        params["period2"] = int(datetime.timestamp(end))
    else:
        params["range"] = period

    params["interval"] = interval
    params["includePrePost"] = True
    params["events"] = "div,splits"
    resp = await client.get(
        url=f"{config.YF_BASE_URL}/v8/finance/chart/{ticker}",
        params=params,
        headers=YAHOO_FINANCE_HEADERS,
    )
    response = resp.json()

    error = response.get("chart", {}).get("error")
    if error:
        logger.error(f"Error response from Y-Finance [{ticker}]: {error}")
        raise HTTPError(error)

    result = response.get("chart", {}).get("result", [])
    if not len(result):
        logger.error(
            f"Empty response from Y-Finance [{ticker}]: period={period} | "
            f"interval={interval} | start={start} | end={end}"
        )
        raise HTTPError(f"Empty response: {response}")
    data = result[0]
    timestamps = data.get("timestamp")
    if not timestamps:
        logger.error(
            f"Empty quotes from Y-Finance [{ticker}]: period={period} | "
            f"interval={interval} | start={start} | end={end}"
        )
        raise HTTPError(f"Empty quotes: {response}")

    ohlc = data["indicators"]["quote"][0]
    bars = Bars(
        __root__=[
            Bar(
                timestamp=timestamp,
                close=close if close is not None else np.nan,
                high=high if high is not None else np.nan,
                low=low if low is not None else np.nan,
                open=open if open is not None else np.nan,
                volume=volume if volume is not None else np.nan,
                interval=interval,
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
