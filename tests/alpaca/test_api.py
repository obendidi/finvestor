from unittest import mock

from alpaca_trade_api.rest import Asset

from finvestor.alpaca import AlpacaClient
from finvestor.alpaca.api import REST


def test_alpca_client_crendentials():
    client = AlpacaClient()
    assert client._client._key_id == "some-made-up-api-key"
    assert client._client._secret_key == "some-made-up-secret-key"
    assert client._client._base_url == "https://paper-api.alpaca.markets"


def test_alpaca_client_reused_between_class_instances():
    client1 = AlpacaClient()
    client2 = AlpacaClient()

    assert id(client1._client) == id(client2._client)


def test_alpaca_client__getattr___get_asset(alpaca_assets):

    ticker = "TSLA"
    with mock.patch.object(REST, "_one_request", return_value=alpaca_assets[ticker]):
        client = AlpacaClient()
        asset = client.get_asset(ticker)
    assert isinstance(asset, Asset)
    assert asset._raw == alpaca_assets[ticker]
