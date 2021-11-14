import httpx
import pytest

from finvestor.yfinance.api import YFClient, YFSettings
from finvestor.schemas import Asset


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
async def test_yf_client_get_asset(respx_mock, yf_scrape_response):
    yf_client = YFClient()
    ticker = "TSLA"
    url = f"{yf_client._settings.YAHOO_FINANCE_SCRAPE_URL}/{ticker}"
    mocked = respx_mock.get(url).mock(
        return_value=httpx.Response(200, text=yf_scrape_response)
    )

    asset = await yf_client.get_asset(ticker)

    assert mocked.called
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
    }
