import logging
import typing as tp
from datetime import datetime, timedelta
from urllib.parse import urljoin

import pytz
from httpx import AsyncClient
from pydantic import root_validator, validate_arguments, validator

from finvestor import config
from finvestor.core.timeframe import TimeFrame
from finvestor.data_providers.alpaca.auth import auth
from finvestor.data_providers.exceptions import EmptyBars
from finvestor.data_providers.schemas import Bar, Bars, BarsRequestParams
from finvestor.data_providers.utils import (
    get_closest_value_to_timedelta,
    parse_duration,
)

logger = logging.getLogger(__name__)


ApcaValidIntervals = tp.Literal[
    "1Min", "2Min", "5Min", "15Min", "30Min", "1Hour", "3Hour", "1Day"
]
ApcaTickerTypes = tp.Literal["stock", "crypto"]
APCA_VALID_INTERVALS: tp.Tuple[ApcaValidIntervals, ...] = tp.get_args(
    ApcaValidIntervals
)
APCA_INTERVAL_MAP: tp.Mapping[timedelta, ApcaValidIntervals] = {
    parse_duration(interval): interval for interval in APCA_VALID_INTERVALS
}
APCA_TICKER_TYPE_TO_URLPATH: tp.Dict[ApcaTickerTypes, str] = {
    "crypto": "/v1beta1/crypto/{ticker}/bars",
    "stock": "/v2/stocks/{ticker}/bars",
}


class AlpacaBarsRequestParams(BarsRequestParams):
    interval: TimeFrame[ApcaValidIntervals] = TimeFrame("1Min")
    historical_data_delay: timedelta = timedelta(0)
    limit: int = 10000
    adjustment: tp.Literal["raw", "split", "dividend", "all"] = "all"

    @validator("interval", pre=True)
    def convert_interval(cls, interval: TimeFrame) -> TimeFrame:
        if not isinstance(interval, TimeFrame):
            interval = TimeFrame(interval)
        if interval.duration in APCA_VALID_INTERVALS:
            return interval
        duration = get_closest_value_to_timedelta(
            APCA_INTERVAL_MAP, parse_duration(interval.duration)
        )
        return TimeFrame(duration)

    @root_validator
    def convert_period_to_start_end(cls, values):
        start = values.get("start")
        end = values.get("end")
        valid_delay: timedelta = values["historical_data_delay"]
        now = pytz.utc.localize(datetime.utcnow())
        if start is not None and end is not None:
            delta_delay = now - end
            if valid_delay.total_seconds() > 0 and delta_delay <= valid_delay:
                raise ValueError(
                    "Provided 'end' value does not respect ALPACA historical data delay"
                    f", provided end={end} has a diff of {delta_delay} < {valid_delay}"
                )
            return values

        # TODO: doesn't take into account days were the market is not Open
        # (holidays, weekends, ..)
        # maybe have a look at: https://github.com/rsheftel/pandas_market_calendars
        period: TimeFrame = values.get("period")
        if period is not None:
            end = now - valid_delay
            start = end - parse_duration(period.duration)
            return {**values, "start": start, "end": end}
        return values

    def __call__(
        self,
        ticker_type: ApcaTickerTypes = "stock",
    ) -> tp.Dict[str, tp.Union[str, int]]:
        assert self.start is not None
        assert self.end is not None
        assert ticker_type in tp.get_args(ApcaTickerTypes)
        params = {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "limit": self.limit,
            "timeframe": self.interval.duration,
        }
        if ticker_type == "stock":
            params["adjustment"] = self.adjustment

        return params


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def get_alpaca_bars(
    ticker: str,
    request_params: tp.Union[BarsRequestParams, tp.Dict[str, tp.Any]],
    *,
    historical_data_delay: timedelta = config.APCA_HISTORICAL_DATA_DELAY,
    client: AsyncClient,
    ticker_type: ApcaTickerTypes = "stock",
) -> Bars:

    if isinstance(request_params, BarsRequestParams):
        request_params = request_params.dict()

    alpaca_request_params = AlpacaBarsRequestParams(
        **request_params, historical_data_delay=historical_data_delay
    )
    alpaca_request_params_dict = alpaca_request_params(ticker_type=ticker_type)
    logger.debug(
        f"[ALPACA] Getting data for ticker '{ticker}' ({ticker_type}) "
        f"with params: {alpaca_request_params_dict}"
    )

    urlpath = APCA_TICKER_TYPE_TO_URLPATH[ticker_type].format(ticker=ticker)

    url = urljoin(config.APCA_API_DATA_URL, urlpath)

    bars: tp.List[tp.Dict[str, tp.Any]] = []
    next_page_token = ""
    while next_page_token is not None:
        if next_page_token:
            alpaca_request_params_dict["page_token"] = next_page_token
        resp = await client.get(url, auth=auth, params=alpaca_request_params_dict)
        if resp.status_code != 200:
            logger.error(
                f"Alpaca (ticker={ticker}) responded with code <{resp.status_code}>: "
                f"{resp.json()}"
            )
            resp.raise_for_status()
        response = resp.json()
        next_page_token = response.get("next_page_token")
        resp_bars = response.get("bars", [])
        if not bars and not resp_bars:
            raise EmptyBars(ticker, response)
        if resp_bars is not None:
            bars.extend(resp_bars)

    return Bars(
        __root__=[
            Bar(
                timestamp=_bar["t"],
                close=_bar["c"],
                high=_bar["h"],
                low=_bar["l"],
                open=_bar["o"],
                volume=_bar["v"],
                interval=alpaca_request_params.interval.duration,
            )
            for _bar in bars
        ]
    )
