from unittest import mock

import pytest

from finvestor.data.yfinance.scrapper import get_asset, get_isin, get_quote_summary
from finvestor.models import Asset


@pytest.mark.default_cassette("data-yfinance-tsla-html-response.yaml")
@pytest.mark.vcr
async def test_get_quote_summary(async_client, snapshot):
    quote_summary = await get_quote_summary("TSLA", client=async_client)
    assert quote_summary == snapshot(name="TSLA")


@pytest.mark.default_cassette("data-yfinance-tsla-isin-response.yaml")
@pytest.mark.vcr
async def test_get_isin(async_client):
    isin = await get_isin("TSLA", client=async_client)
    assert isin == "US88160R1014"


@pytest.mark.parametrize("ticker", ["ETH-USD", "^QQQ"])
async def test_get_isin_none(async_client, ticker):
    isin = await get_isin(ticker, client=async_client)
    assert isin is None


@pytest.mark.default_cassette("data-yfinance-tsla-html-response.yaml")
@pytest.mark.vcr
@pytest.mark.parametrize("isin", [None, "US88160R1014"])
async def test_get_asset(async_client, isin):
    with mock.patch(
        "finvestor.data.yfinance.scrapper.get_isin", return_value=isin
    ) as mocked:
        asset = await get_asset("TSLA", client=async_client)

    assert isinstance(asset, Asset)
    mocked.assert_awaited_once_with("TSLA", client=async_client)
    assert asset.dict() == {
        "ticker": "TSLA",
        "name": "Tesla, Inc.",
        "type": "EQUITY",
        "currency": "USD",
        "exchange": "NMS",
        "exchange_timezone": "America/New_York",
        "market": "us_market",
        "country": "United States",
        "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers",
        "isin": isin,
    }
