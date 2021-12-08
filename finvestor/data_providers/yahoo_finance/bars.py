import asyncio
import logging
import typing as tp
from datetime import datetime

import numpy as np
from httpx import (
    AsyncClient,
    ConnectTimeout,
    HTTPError,
    HTTPStatusError,
    Request,
    Response,
)
from tenacity import TryAgain, before_sleep_log, retry, wait_exponential, wait_random

from finvestor.schemas.bar import Bar, Bars
from finvestor.data_providers.yahoo_finance.utils import (
    AutoValidInterval,
    ValidPeriod,
    YFBarsRequestParams,
    get_valid_intervals,
    user_agent_header,
    YF_CHART_URI,
)

logger = logging.getLogger(__name__)


class YahooFinanceInvalidResponse(HTTPError):
    def __init__(self, message: str, *, request: Request, response: Response) -> None:
        super().__init__(message)
        self.request = request
        self.response = response


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10) + wait_random(0, 2),
    before_sleep=before_sleep_log(logger, logging.DEBUG),
)
async def get_yahoo_finance_ticker_ohlc(
    ticker: str,
    *,
    params: YFBarsRequestParams,
    client: AsyncClient,
) -> tp.Dict[str, tp.List[tp.Union[None, float, int]]]:

    logger.debug(
        f"[YF] GET '{ticker}' bars with params: "
        f"{params.dict(by_alias=True, exclude_none=True)}."
    )
    try:
        resp = await client.get(
            url=YF_CHART_URI.format(ticker=ticker),
            params=params.dict(exclude_none=True, by_alias=True),
            headers=user_agent_header(),
        )
    except ConnectTimeout as timeout_error:
        logger.error(f"ConnectTimeout: {timeout_error}")
        raise TryAgain(f"{str(timeout_error)}") from timeout_error

    resp.raise_for_status()
    response = resp.json()

    request = resp._request
    assert request is not None

    result = response.get("chart", {}).get("result", [])
    error = response.get("chart", {}).get("error")
    if error:
        raise YahooFinanceInvalidResponse(
            f"Yahoo finance responded with chart error: {error}",
            request=request,
            response=resp,
        )
    if not result or not isinstance(result, list):
        raise YahooFinanceInvalidResponse(
            f"Yahoo finance responded with empty/invalid chart result: {result}",
            request=request,
            response=resp,
        )

    timestamp = result[0].get("timestamp")
    if not timestamp:
        raise YahooFinanceInvalidResponse(
            f"Yahoo finance responded with empty quotes: {result}",
            request=request,
            response=resp,
        )
    try:
        ohlc = result[0]["indicators"]["quote"][0]
        return dict(timestamp=timestamp, **ohlc)
    except KeyError as error:
        raise YahooFinanceInvalidResponse(
            f"{error}", request=request, response=resp
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
    events: tp.Literal[None, "div", "split", "div,splits"] = "div,splits",
) -> Bars:

    params = YFBarsRequestParams(
        interval=interval,
        period=period,
        start=start,
        end=end,
        include_prepost=include_prepost,
        events=events,
    )

    if params.interval == "auto":
        valid_intervals = get_valid_intervals(params)
    else:
        valid_intervals = (params.interval,)

    errors = []
    for valid_interval in valid_intervals:
        try:
            if params.interval != valid_interval:
                logger.debug(
                    f"[YF] (ticker='{ticker}'): "
                    f"(auto-)updating interval from '{params.interval}' "
                    f"to '{valid_interval}'."
                )
                params.interval = valid_interval
            ohlc = await get_yahoo_finance_ticker_ohlc(
                ticker,
                params=params,
                client=client,
            )
            break
        except HTTPStatusError as error:
            if error.response.status_code == 422:
                logger.error(
                    f"Client error '422 Unprocessable Entity': {error.response.json()}"
                )
                errors.append(error)
                continue
            raise error
    else:
        if len(errors) == 1:
            raise errors[0]
        raise HTTPError(
            f"[YF] (ticker='{ticker}') "
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
                ohlc["timestamp"],
                ohlc["volume"],
                ohlc["open"],
                ohlc["close"],
                ohlc["low"],
                ohlc["high"],
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
    events: tp.Literal[None, "div", "split", "div,splits"] = "div,splits",
) -> tp.Dict[str, Bars]:
    if isinstance(tickers, str):
        tickers = tickers.split(",")

    bars = await asyncio.gather(
        *[
            get_yahoo_finance_ticker_bars(
                ticker,
                client=client,
                interval=interval,
                period=period,
                start=start,
                end=end,
                include_prepost=include_prepost,
                events=events,
            )
            for ticker in tickers
        ]
    )
    return dict(zip(tickers, bars))


if __name__ == "__main__":

    params = YFBarsRequestParams(interval="auto", period="1mo")
    ticker = "TSLA,AAPL"

    async def main():
        async with AsyncClient() as client:
            bars = await get_yahoo_finance_bars(
                ticker, client=client, period="1d", interval="1h"
            )
        print(bars)

    asyncio.run(main())
