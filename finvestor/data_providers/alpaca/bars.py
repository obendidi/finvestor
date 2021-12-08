import logging
import typing as tp
from datetime import datetime, timedelta
from urllib.parse import urljoin

import pytz
from httpx import AsyncClient

from finvestor.data_providers.alpaca.auth import auth
from finvestor.data_providers.alpaca.schemas import APCABarsRequestParams
from finvestor.data_providers.alpaca.settings import alpaca_settings
from finvestor.data_providers.exceptions import EmptyBars
from finvestor.data_providers.schemas import AutoValidInterval, Bar, Bars, ValidPeriod

logger = logging.getLogger(__name__)


ApcaTickerTypes = tp.Literal["stock", "crypto"]

APCA_TICKER_TYPE_TO_URLPATH: tp.Dict[ApcaTickerTypes, str] = {
    "crypto": "/v1beta1/crypto/{tickers}/bars",
    "stock": "/v2/stocks/{tickers}/bars",
}


async def _get_bars(
    tickers: tp.Union[str, tp.List[str]],
    *,
    params: APCABarsRequestParams,
    client: AsyncClient,
    end_default: tp.Literal["now", "interval"] = "now",
    ticker_type: ApcaTickerTypes = "stock",
):
    urlpath = APCA_TICKER_TYPE_TO_URLPATH[ticker_type].format(tickers=tickers)
    url = urljoin(alpaca_settings.DATA_URL, urlpath)
    request_params = params.params(end_default=end_default)
    bars: tp.List[tp.Dict[str, tp.Any]] = []
    next_page_token = ""
    while next_page_token is not None:
        if next_page_token:
            request_params["page_token"] = next_page_token
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


async def get_alpaca_bars(
    tickers: tp.Union[str, tp.List[str]],
    *,
    client: AsyncClient,
    interval: AutoValidInterval = "auto",
    period: tp.Optional[ValidPeriod] = None,
    start: tp.Optional[datetime] = None,
    end: tp.Optional[datetime] = None,
    limit: int = 1000,
    adjustment: tp.Literal[None, "raw", "split", "dividend", "all"] = None,
    end_default: tp.Literal["now", "interval"] = "now",
) -> tp.Union[Bars, tp.Dict[str, Bars]]:

    if isinstance(tickers, list):
        tickers = ",".join(tickers)

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
