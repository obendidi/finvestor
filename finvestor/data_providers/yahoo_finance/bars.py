import asyncio
import logging
import random
import typing as tp
from datetime import datetime, timedelta

import numpy as np
import pytz
from httpx import AsyncClient, HTTPError

from finvestor.data_providers.exceptions import (
    BaseHTTPError,
    EmptyBars,
    UnprocessableEntity,
)
from finvestor.data_providers.schemas import (
    AutoValidInterval,
    Bar,
    Bars,
    ValidInterval,
    ValidPeriod,
)
from finvestor.data_providers.yahoo_finance.schemas import (
    YFBarsRequestParams,
    YfOpenHighLowClose,
)
from finvestor.data_providers.yahoo_finance.utils import get_valid_intervals
from finvestor.yahoo_finance.api.headers import USER_AGENT_LIST
from finvestor.yahoo_finance.settings import yf_settings

logger = logging.getLogger(__name__)


async def get_yahoo_finance_ticker_ohlc(
    ticker: str,
    *,
    params: YFBarsRequestParams,
    client: AsyncClient,
    interval: ValidInterval,
    end_default: tp.Literal["now", "interval"] = "now",
) -> YfOpenHighLowClose:
    request_params = params.params(end_default=end_default, interval=interval)
    resp = await client.get(
        url=f"{yf_settings.BASE_URL}/v8/finance/chart/{ticker.upper()}",
        params=request_params,
        headers={"User-Agent": random.choice(USER_AGENT_LIST)},
    )
    if resp.status_code == 422:
        raise UnprocessableEntity(
            ticker=ticker,
            params=request_params,
            status_code=resp.status_code,
            error=resp.json(),
            data_provider="yahoo_finance",
        )
    response = resp.json()
    result = response.get("chart", {}).get("result", [])
    error = response.get("chart", {}).get("error")
    if not result or error or not isinstance(result, list):
        raise BaseHTTPError(
            ticker=ticker,
            params=request_params,
            status_code=resp.status_code,
            error=resp.json(),
            data_provider="yahoo_finance",
        )
    timestamp = result[0].get("timestamp")
    if not timestamp:
        raise EmptyBars(
            ticker=ticker,
            params=request_params,
            status_code=resp.status_code,
            error="Empty bars",
            data_provider="yahoo_finance",
        )
    try:
        ohlc = result[0]["indicators"]["quote"][0]
        return YfOpenHighLowClose(timestamp=timestamp, **ohlc)
    except KeyError as error:
        raise BaseHTTPError(
            ticker=ticker,
            params=request_params,
            status_code=resp.status_code,
            error=error,
            data_provider="yahoo_finance",
        ) from error


async def get_yahoo_finance_ticker_bars(
    ticker: str,
    *,
    client: AsyncClient,
    interval: AutoValidInterval = "auto",
    period: tp.Optional[ValidPeriod] = None,
    start: tp.Optional[datetime] = None,
    end: tp.Optional[datetime] = None,
    include_prepost: tp.Optional[bool] = None,
    events: tp.Literal[None, "div", "split", "div,splits"] = None,
    end_default: tp.Literal["now", "interval"] = "now",
) -> Bars:
    params = YFBarsRequestParams(
        interval=interval,
        period=period,
        start=start,
        end=end,
        include_prepost=include_prepost,
        events=events,
    )
    if interval == "auto":
        valid_intervals = get_valid_intervals(period=period, start=start)
    else:
        valid_intervals = (interval,)

    errors = []
    for valid_interval in valid_intervals:
        try:
            if interval != valid_interval:
                logger.debug(
                    f"[YAHOO_FINANCE] (ticker={ticker}): "
                    f"(auto-)updating interval from '{interval}' to '{valid_interval}'."
                )
                interval = valid_interval
            ohlc = await get_yahoo_finance_ticker_ohlc(
                ticker,
                params=params,
                client=client,
                interval=valid_interval,
                end_default=end_default,
            )
            break
        except (UnprocessableEntity, EmptyBars) as error:
            logger.error(error)
            errors.append(error)
    else:
        if len(errors) == 1:
            raise errors[0]
        raise HTTPError(
            f"[YAHOO_FINANCE] (ticker={ticker}) "
            f"(valid_intervals={valid_intervals}) responded with:\n{errors}"
        )

    bars = Bars(
        __root__=[
            Bar(
                timestamp=timestamp,
                close=close if close is not None else np.nan,
                high=high if high is not None else np.nan,
                low=low if low is not None else np.nan,
                open=open if open is not None else np.nan,
                volume=volume if volume is not None else np.nan,
                interval=valid_interval,
            )
            for timestamp, volume, open, close, low, high in zip(
                ohlc.timestamp,
                ohlc.volume,
                ohlc.open,
                ohlc.close,
                ohlc.low,
                ohlc.high,
            )
        ]
    )
    return bars


async def get_yahoo_finance_bars(
    tickers: tp.Union[str, tp.List[str]],
    *,
    client: AsyncClient,
    interval: AutoValidInterval = "auto",
    period: tp.Optional[ValidPeriod] = None,
    start: tp.Optional[datetime] = None,
    end: tp.Optional[datetime] = None,
    include_prepost: tp.Optional[bool] = None,
    events: tp.Literal[None, "div", "split", "div,splits"] = None,
    end_default: tp.Literal["now", "interval"] = "now",
) -> tp.Union[Bars, tp.Dict[str, Bars]]:
    if isinstance(tickers, str):
        tickers = tickers.split(",")

    bars = await asyncio.gather(
        *[
            get_yahoo_finance_ticker_bars(
                ticker,
                client=client,
                start=start,
                end=end,
                period=period,
                interval=interval,
                include_prepost=include_prepost,
                events=events,
                end_default=end_default,
            )
            for ticker in tickers
        ]
    )
    if len(bars) == 1:
        return bars[0]
    return dict(zip(tickers, bars))


if __name__ == "__main__":

    async def main():
        async with AsyncClient() as client:
            end = datetime.now(tz=pytz.UTC) - timedelta(hours=15)
            start = datetime.now(tz=pytz.UTC) - timedelta(hours=18)
            result = await get_yahoo_finance_bars(
                ["TSLA", "AAPL"], start=start, end=end, client=client
            )
            for ticker, bars in result.items():
                print(ticker)
                print(bars.df().head(5))

    asyncio.run(main())
