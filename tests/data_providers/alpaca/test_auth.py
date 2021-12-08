import pytest
from httpx import Request

from finvestor import config
from finvestor.data_providers.alpaca.auth import auth


@pytest.fixture
def mocked_config():
    # store default values
    default_data_provider = config.DATA_PROVIDER
    default_key_id = config.APCA_API_KEY_ID
    default_secret_id = config.APCA_API_SECRET_KEY

    # update defaults
    config.DATA_PROVIDER = "alpaca"
    config.APCA_API_KEY_ID = "test-key-id-xxxx"
    config.APCA_API_SECRET_KEY = "test-secretd-id-yyyyy"
    yield
    # restore old values
    config.DATA_PROVIDER = default_data_provider
    config.APCA_API_KEY_ID = default_key_id
    config.APCA_API_SECRET_KEY = default_secret_id


def test_auth(mocked_config):

    request = auth(Request("POST", "http://testurl"))
    assert request.headers["apca-api-key-id"] == "test-key-id-xxxx"
    assert request.headers["apca-api-secret-key"] == "test-secretd-id-yyyyy"
