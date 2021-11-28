import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin

import pytz
from httpx import AsyncClient, HTTPError
from pydantic import validate_arguments

from finvestor.core import config
from finvestor.data_providers.alpaca.auth import auth
from finvestor.data_providers.schemas import Bar, Bars
from finvestor.data_providers.utils import (
    ValidInterval,
    ValidPeriod,
    time_period_to_timedelta,
    validate_start_end_period_args,
    DEFAULT_INTERVAL,
)

logger = logging.getLogger(__name__)


def _interval_to_apca_timeframe(interval: ValidInterval) -> str:
    if interval.endswith("m"):
        return str(interval.replace("m", "Min"))
    elif interval.endswith("h"):
        return str(interval.replace("h", "Hour"))
    elif interval.endswith("d"):
        return str(interval.replace("d", "Day"))
    elif interval.endswith("mo"):
        return str(interval.replace("mo", "Month"))
    raise ValueError(f"Unsupported interval: {interval}")


def is_before_apca_historical_delay(end: datetime) -> bool:
    if config.APCA_HISTORICAL_DATA_DELAY_SECONDS.total_seconds() == 0:
        return True
    now = pytz.utc.localize(datetime.utcnow())
    delta = now - end
    if delta <= config.APCA_HISTORICAL_DATA_DELAY_SECONDS:
        return False
    return True


def _validate_apca_start_end_args(
    ticker: str,
    period: Optional[ValidPeriod] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Tuple[datetime, datetime]:
    period, start, end = validate_start_end_period_args(
        period=period, start=start, end=end
    )
    if period is not None:
        delta = time_period_to_timedelta(period)
        # in alpaca free tier we can't get last 15 minutes
        end = pytz.utc.localize(datetime.utcnow())
        if config.APCA_HISTORICAL_DATA_DELAY_SECONDS.total_seconds() > 0:
            logger.debug(
                f"ALPACA - '{ticker}' - Appting delay of "
                f"{config.APCA_HISTORICAL_DATA_DELAY_SECONDS} minutes for alpaca "
                "historical data."
            )
            end = end - config.APCA_HISTORICAL_DATA_DELAY_SECONDS
        start = end - delta
    elif start is not None and end is not None:
        if not is_before_apca_historical_delay(end):
            raise ValueError(
                f"Provided alpaca config limits historical data with a delay of "
                f"{config.APCA_HISTORICAL_DATA_DELAY_SECONDS}, end date: {end} does not"
                f"support that delay."
            )
    else:
        raise NotImplementedError()

    return start, end


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_alpaca_bars(
    ticker: str,
    *,
    client: AsyncClient,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    period: Optional[ValidPeriod] = None,
    interval: ValidInterval = DEFAULT_INTERVAL,
) -> Optional[Bars]:
    start, end = _validate_apca_start_end_args(
        ticker, period=period, start=start, end=end
    )

    params: Dict[str, Any] = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "timeframe": _interval_to_apca_timeframe(interval),
        "limit": 10000,
    }
    if "-" in ticker:
        urlpath = f"/v1beta1/crypto/{ticker.replace('-', '')}/bars"
    else:
        urlpath = f"/v2/stocks/{ticker}/bars"
        params["adjustment"] = "all"
    url = urljoin(config.APCA_API_DATA_URL, urlpath)

    bars = []
    next_page_token = ""
    while next_page_token is not None:
        if next_page_token:
            params["page_token"] = next_page_token
        try:
            resp = await client.get(url, auth=auth, params=params)
            resp.raise_for_status()
        except HTTPError as error:
            logger.error(f"ALPACA - '{ticker}' - {error}")
            raise HTTPError(str(error)) from error
        response = resp.json()
        _bars = response.get("bars")
        next_page_token = response.get("next_page_token")
        if _bars:
            bars.extend(_bars)
    if not bars:
        logger.debug(
            f"ALPACA - '{ticker}' - Got empty response, asset not found. "
            f"(urlpath={urlpath})"
        )
        return None
    return Bars(
        __root__=[
            Bar(
                timestamp=_bar["t"],
                close=_bar["c"],
                high=_bar["h"],
                low=_bar["l"],
                open=_bar["o"],
                volume=_bar["v"],
                interval=interval,
            )
            for _bar in bars
        ]
    )


if __name__ == "__main__":
    import asyncio

    async def _main():
        async with AsyncClient() as client:
            bars = await get_alpaca_bars(
                "DOYU", client=client, period="1d", interval="30m"
            )
            print(bars.df())

    asyncio.run(_main())