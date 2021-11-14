import logging
from typing import Any, Dict

import attr
import httpx

from finvestor.schemas import Asset
from finvestor.yfinance.settings import USER_AGENT_HEADERS, YFSettings
from finvestor.yfinance.utils import parse_quote_summary

logger = logging.getLogger(__name__)


@attr.s
class YFClient:
    _client = attr.ib(default=httpx.AsyncClient(headers=USER_AGENT_HEADERS), init=False)
    _settings: YFSettings = attr.ib(kw_only=True, factory=YFSettings)

    async def aclose(self):
        return await self._client.aclose()

    async def get_asset(self, ticker: str) -> Asset:
        """Get asset information of provided ticker.

        Args:
            ticker: ticker of an asset availlable in yahoo finance.

        Returns:
            Asset
        """
        summary = await self.get_quote_summary(ticker)
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
