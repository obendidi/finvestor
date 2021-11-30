import logging
import typing as tp
from datetime import datetime

from httpx import AsyncClient
from pydantic import validate_arguments

from finvestor import config
from finvestor.data_providers.schemas import (
    AutoValidInterval,
    Bar,
    Bars,
    ValidInterval,
    ValidPeriod,
)
from finvestor.data_providers.utils import (
    get_closest_price_to_timestamp_from_bar,
    get_smallest_valid_period_for_interval,
)
from finvestor.data_providers.yahoo_finance.bars import get_yahoo_finance_bars

logger = logging.getLogger(__name__)


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_bars(
    tickers: tp.Union[str, tp.List[str]],
    *,
    client: AsyncClient,
    interval: AutoValidInterval = "auto",
    period: tp.Optional[ValidPeriod] = None,
    start: tp.Optional[datetime] = None,
    end: tp.Optional[datetime] = None,
    end_default: tp.Literal["now", "interval"] = "now",
) -> tp.Union[Bars, tp.Dict[str, Bars]]:

    if config.MARKET_DATA_PROVIDER == "alpaca":
        raise NotImplementedError()

    return await get_yahoo_finance_bars(
        tickers,
        client=client,
        interval=interval,
        period=period,
        start=start,
        end=end,
        end_default=end_default,
        include_prepost=True,
        events="div,splits",
    )


async def get_latest_bar(
    tickers: tp.Union[str, tp.List[str]],
    *,
    client: AsyncClient,
    interval: ValidInterval = "1m",
) -> tp.Union[Bar, tp.Dict[str, Bar]]:

    allbars = await get_bars(
        tickers,
        client=client,
        interval=interval,
        period=get_smallest_valid_period_for_interval(interval),
    )
    if isinstance(allbars, Bars):
        return allbars[-1]

    return {ticker: bars[-1] for ticker, bars in allbars.items()}


async def get_bar_at_timestamp(
    tickers: tp.Union[str, tp.List[str]],
    *,
    client: AsyncClient,
    timestamp: datetime,
) -> tp.Union[Bar, tp.Dict[str, Bar]]:

    start = timestamp.replace(second=0)

    allbars = await get_bars(
        tickers, client=client, start=start, interval="auto", end_default="interval"
    )
    if isinstance(allbars, Bars):
        return allbars[0]

    return {ticker: bars[0] for ticker, bars in allbars.items()}


async def get_price_at_timestamp(
    tickers: tp.Union[str, tp.List[str]],
    *,
    client: AsyncClient,
    timestamp: datetime,
) -> tp.Union[float, tp.Dict[str, float]]:
    allbars = await get_bar_at_timestamp(tickers, client=client, timestamp=timestamp)
    if isinstance(allbars, Bar):
        return get_closest_price_to_timestamp_from_bar(allbars, timestamp)
    return {
        ticker: get_closest_price_to_timestamp_from_bar(bar, timestamp)
        for ticker, bar in allbars.items()
    }


if __name__ == "__main__":
    import asyncio
    from datetime import timedelta

    import pytz

    ticker = "TSLA,AAPL"

    async def main():
        async with AsyncClient() as client:
            bars = await get_price_at_timestamp(
                ticker,
                client=client,
                timestamp=datetime.now(tz=pytz.utc) - timedelta(minutes=2),
            )

        print(bars)

    asyncio.run(main())
