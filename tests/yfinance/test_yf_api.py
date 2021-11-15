from urllib.parse import quote

import httpx
import pytest

from finvestor.schemas import Asset
from finvestor.yfinance.api import YFClient, YFSettings


def test_yf_client_custom_settings():
    settings = YFSettings(
        YAHOO_FINANCE_SCRAPE_URL="https://this-is-not-finacial-advice",
        YAHOO_FINANCE_BASE_URL="https://this-is-finacial-advice",
    )
    client = YFClient(settings=settings)

    assert (
        client._settings.YAHOO_FINANCE_SCRAPE_URL
        == "https://this-is-not-finacial-advice"
    )
    assert client._settings.YAHOO_FINANCE_BASE_URL == "https://this-is-finacial-advice"


def test_yf_client_httpx_not_init():
    with httpx.Client() as _client:
        with pytest.raises(
            TypeError, match=r"__init__\(\) got an unexpected keyword argument 'client'"
        ):
            YFClient(client=_client)


@pytest.mark.anyio
async def test_yf_client_get_quote_summary(
    respx_mock, yf_scrape_response, quote_summary_snapshot
):
    yf_client = YFClient()
    ticker = "TSLA"
    url = f"{yf_client._settings.YAHOO_FINANCE_SCRAPE_URL}/{ticker}"
    mocked = respx_mock.get(url).mock(
        return_value=httpx.Response(200, text=yf_scrape_response)
    )

    parsed = await yf_client.get_quote_summary(ticker)
    assert mocked.called
    assert parsed == quote_summary_snapshot


@pytest.mark.anyio
async def test_yf_client_get_isin(respx_mock, isin_scrape_response):
    yf_client = YFClient()
    ticker = "TSLA"
    short_name = "Tesla Inc."
    isin_mocked = respx_mock.get(
        f"{yf_client._settings.ISIN_SCRAPE_URL}?"
        f"max_results={yf_client._settings.ISIN_SCRAPE_MAX_RESULTS}"
        f"&query={quote(short_name)}",
    ).mock(return_value=httpx.Response(200, text=isin_scrape_response))

    isin = await yf_client.get_isin(ticker, short_name=short_name)
    assert isin == "US88160R1014"
    assert isin_mocked.called


@pytest.mark.anyio
async def test_yf_client_get_isin_None(respx_mock, isin_scrape_response):
    yf_client = YFClient()
    ticker = "BTC-USD"
    short_name = "Bitcoin."
    isin_mocked = respx_mock.get(
        f"{yf_client._settings.ISIN_SCRAPE_URL}?"
        f"max_results={yf_client._settings.ISIN_SCRAPE_MAX_RESULTS}"
        f"&query={quote(short_name)}",
    ).mock(return_value=httpx.Response(200, text=isin_scrape_response))

    isin = await yf_client.get_isin(ticker, short_name=short_name)
    assert isin is None
    assert not isin_mocked.called


@pytest.mark.anyio
async def test_yf_client_get_isin_not_found(respx_mock, isin_scrape_response):
    yf_client = YFClient()
    ticker = "BTC"
    short_name = "Bitcoin."
    isin_mocked = respx_mock.get(
        f"{yf_client._settings.ISIN_SCRAPE_URL}?"
        f"max_results={yf_client._settings.ISIN_SCRAPE_MAX_RESULTS}"
        f"&query={quote(short_name)}",
    ).mock(return_value=httpx.Response(200, text=isin_scrape_response))

    isin = await yf_client.get_isin(ticker, short_name=short_name)
    assert isin is None
    assert isin_mocked.called


@pytest.mark.anyio
async def test_connection_error(respx_mock):
    yf_client = YFClient()
    ticker = "TSLA"
    short_name = "Tesla Inc."
    url = (
        f"{yf_client._settings.ISIN_SCRAPE_URL}?"
        f"max_results={yf_client._settings.ISIN_SCRAPE_MAX_RESULTS}"
        f"&query={quote(short_name)}"
    )
    isin_mocked = respx_mock.get(url).mock(side_effect=httpx.ConnectError)

    isin = await yf_client.get_isin(ticker, short_name=short_name)
    assert isin is None
    assert isin_mocked.called


@pytest.mark.anyio
async def test_yf_client_get_asset_without_isin(respx_mock, yf_scrape_response):
    yf_client = YFClient()
    ticker = "TSLA"
    yf_url = f"{yf_client._settings.YAHOO_FINANCE_SCRAPE_URL}/{ticker}"
    yf_mocked = respx_mock.get(yf_url).mock(
        return_value=httpx.Response(200, text=yf_scrape_response)
    )

    asset = await yf_client.get_asset(ticker)

    assert yf_mocked.called
    assert isinstance(asset, Asset)
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
        "isin": None,
    }


@pytest.mark.anyio
async def test_yf_client_get_asset_with_isin(
    respx_mock, yf_scrape_response, isin_scrape_response
):
    yf_client = YFClient()
    ticker = "TSLA"
    yf_url = f"{yf_client._settings.YAHOO_FINANCE_SCRAPE_URL}/{ticker}"
    yf_mocked = respx_mock.get(yf_url).mock(
        return_value=httpx.Response(200, text=yf_scrape_response)
    )
    isin_mocked = respx_mock.get(
        f"{yf_client._settings.ISIN_SCRAPE_URL}?"
        f"max_results={yf_client._settings.ISIN_SCRAPE_MAX_RESULTS}"
        f"&query=Tesla%2C+Inc.",
    ).mock(return_value=httpx.Response(200, text=isin_scrape_response))

    asset = await yf_client.get_asset(ticker, with_isin=True)

    assert yf_mocked.called
    assert isin_mocked.called
    assert isinstance(asset, Asset)
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
        "isin": "US88160R1014",
    }
