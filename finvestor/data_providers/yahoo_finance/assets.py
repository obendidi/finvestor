import asyncio
import json
import random
from typing import Any, Dict, Optional

from httpx import AsyncClient

from finvestor.data_providers.schemas import Asset
from finvestor.yahoo_finance.api.headers import USER_AGENT_LIST
from finvestor.yahoo_finance.settings import yf_settings


async def get_quote_summary(ticker: str, *, client: AsyncClient) -> Dict[str, Any]:
    """Get quote summary of an ticker.

    Contains a variety of informations:
    [
        'defaultKeyStatistics', 'summaryProfile', 'recommendationTrend',
        'financialsTemplate', 'earnings', 'price', 'financialData', 'quoteType',
        'calendarEvents', 'summaryDetail', 'symbol', 'assetProfile',
        'upgradeDowngradeHistory', 'pageViews'
    ]

    Args:
        ticker: ticker of the asset to get
        client: httpx.AsyncClient

    Returns:
        Dict[str, Any]
    """
    resp = await client.get(
        f"{yf_settings.SCRAPE_URL}/{ticker}",
        headers={"User-Agent": random.choice(USER_AGENT_LIST)},
    )

    resp.raise_for_status()

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


async def get_isin(ticker: str, *, client: AsyncClient) -> Optional[str]:
    """Get ISIN of an asset provided it's ticker or short name.

    Args:
        ticker: Ticker of the asset to get
        short_name: Defaults to None.

    Returns:
        ISIN of the asset or None
    """
    if "-" in ticker or "^" in ticker:
        return None
    resp = await client.get(
        url=yf_settings.ISIN_SCRAPE_URL,
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


async def get_asset(ticker: str, *, client: AsyncClient) -> Asset:
    """Get asset information of provided ticker.

    Args:
        ticker: ticker of an asset availlable in yahoo finance.
        with_isin: wether to query ISIN of the ticker, defaults to false

    Returns:
        Asset
    """
    summary, isin = await asyncio.gather(
        get_quote_summary(ticker, client=client), get_isin(ticker, client=client)
    )
    long_name = summary.get("quoteType", {}).get("longName")
    short_name = summary.get("quoteType", {}).get("shortName")
    name = summary.get("summaryProfile", {}).get("name")

    return Asset(
        ticker=ticker,
        name=long_name or short_name or name,
        type=summary.get("quoteType", {}).get("quoteType"),
        exchange_timezone=summary.get("quoteType", {}).get("exchangeTimezoneName"),
        currency=summary.get("price", {}).get("currency"),
        country=summary.get("summaryProfile", {}).get("country"),
        exchange=summary.get("quoteType", {}).get("exchange"),
        industry=summary.get("summaryProfile", {}).get("industry"),
        sector=summary.get("summaryProfile", {}).get("sector"),
        market=summary.get("quoteType", {}).get("market"),
        isin=isin,
    )
