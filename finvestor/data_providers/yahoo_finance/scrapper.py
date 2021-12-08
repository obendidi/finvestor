import asyncio
import json
import logging
import typing as tp

from httpx import AsyncClient, ConnectTimeout, HTTPStatusError
from tenacity import TryAgain, before_sleep_log, retry, wait_exponential, wait_random

from finvestor.schemas.base import BaseAsset
from finvestor.data_providers.yahoo_finance.utils import (
    user_agent_header,
    YF_QUOTE_URI,
    ISIN_URI,
)

logger = logging.getLogger(__name__)


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10) + wait_random(0, 2),
    before_sleep=before_sleep_log(logger, logging.DEBUG),
)
async def get_quote_summary(
    ticker: str, *, client: AsyncClient
) -> tp.Dict[str, tp.Any]:

    try:
        resp = await client.get(
            YF_QUOTE_URI.format(ticker=ticker), headers=user_agent_header()
        )

        resp.raise_for_status()
    except ConnectTimeout as error:
        logger.error(f"ConnectTimeout: {error}")
        raise TryAgain(f"{str(error)}") from error
    except HTTPStatusError as error:
        if error.response.status_code == 302:
            logger.error(
                f"Ticker '{ticker}' not found in yahoo-finance, it may be "
                "delisted or renamed."
            )
            return {}
        elif error.response.status_code in [502]:
            raise TryAgain(f"{str(error)}") from error
        raise error

    data = json.loads(
        resp.text.split("root.App.main =")[1]
        .split("(this)")[0]
        .split(";\n}")[0]
        .strip()
        .replace("{}", "null")
    )
    quote_symmary_store = (
        data.get("context", {})
        .get("dispatcher", {})
        .get("stores", {})
        .get("QuoteSummaryStore")
    )

    return quote_symmary_store


async def get_isin(ticker: str, *, client: AsyncClient) -> tp.Optional[str]:
    if "-" in ticker or "^" in ticker:
        return None
    resp = await client.get(
        ISIN_URI,
        params={
            "max_results": "25",
            "query": ticker,
        },
    )
    resp.raise_for_status()

    search_str = f'"{ticker}|'
    if search_str not in resp.text:
        return None
    return resp.text.split(search_str)[1].split('"')[0].split("|")[0]


async def get_asset(ticker: str, *, client: AsyncClient) -> BaseAsset:
    summary, isin = await asyncio.gather(
        get_quote_summary(ticker, client=client), get_isin(ticker, client=client)
    )
    summary_profile = summary.get("summaryProfile", {}) or {}
    quote_type = summary.get("quoteType", {}) or {}

    long_name = quote_type.get("longName")
    short_name = quote_type.get("shortName")
    name = summary_profile.get("name")

    return BaseAsset(
        ticker=ticker,
        name=long_name or short_name or name,
        type=quote_type.get("quoteType"),
        exchange_timezone=quote_type.get("exchangeTimezoneName"),
        currency=summary.get("price", {}).get("currency"),
        country=summary_profile.get("country"),
        exchange=quote_type.get("exchange"),
        industry=summary_profile.get("industry"),
        sector=summary_profile.get("sector"),
        market=quote_type.get("market"),
        isin=isin,
    )
