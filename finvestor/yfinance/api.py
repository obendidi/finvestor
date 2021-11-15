import logging
from typing import Any, Dict, Optional, Union

import attr
import httpx

from finvestor.schemas import Asset
from finvestor.yfinance.settings import YF_HEADERS, YFSettings
from finvestor.yfinance.utils import parse_quote_summary

logger = logging.getLogger(__name__)


@attr.s
class YFClient:
    _client = attr.ib(default=httpx.AsyncClient(headers=YF_HEADERS), init=False)
    _settings: YFSettings = attr.ib(kw_only=True, factory=YFSettings)

    async def aclose(self):
        return await self._client.aclose()

    async def get_isin(
        self, ticker: str, short_name: Optional[str] = None
    ) -> Optional[str]:
        """Get ISIN of an asset provided it's ticker or short name.

        Args:
            ticker: Ticker of the asset to get
            short_name: Defaults to None.

        Returns:
            ISIN of the asset or None
        """
        if "-" in ticker or "^" in ticker:
            return None
        params: Dict[str, Union[int, str]] = {
            "max_results": self._settings.ISIN_SCRAPE_MAX_RESULTS,
            "query": short_name or ticker,
        }
        try:
            resp = await self._client.get(
                url=self._settings.ISIN_SCRAPE_URL,
                params=params,
                timeout=self._settings.ISIN_SCRAPE_TIMEOUT,
            )
            resp.raise_for_status()
        except Exception as error:
            logger.error(f"func: get_isin | ticker: {ticker} | error: {error}")
            return None

        search_str = f'"{ticker}|'
        if search_str not in resp.text:
            return None
        return resp.text.split(search_str)[1].split('"')[0].split("|")[0]

    async def get_asset(self, ticker: str, with_isin: bool = False) -> Asset:
        """Get asset information of provided ticker.

        Args:
            ticker: ticker of an asset availlable in yahoo finance.
            with_isin: wether to query ISIN of the ticker, defaults to false

        Returns:
            Asset
        """
        summary = await self.get_quote_summary(ticker)
        long_name = summary.get("quoteType", {}).get("longName")
        short_name = summary.get("quoteType", {}).get("shortName")
        name = summary.get("summaryProfile", {}).get("name")
        isin = await self.get_isin(ticker, short_name=short_name) if with_isin else None

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

    async def get_quote_summary(self, ticker: str) -> Dict[str, Any]:
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

        Returns:
            Dict[str, Any]
        """
        url = f"{self._settings.YAHOO_FINANCE_SCRAPE_URL}/{ticker}"

        resp = await self._client.get(url)

        resp.raise_for_status()

        return parse_quote_summary(resp.text)
