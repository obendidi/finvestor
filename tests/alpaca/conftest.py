from typing import Dict

import pytest

ALPCA_ASSETS = {
    "TSLA": {
        "id": "0",
        "class": "us_equity",
        "exchange": "NASDAQ",
        "symbol": "TSLA",
        "name": "Tesla, Inc. Common Stock",
        "status": "active",
        "tradable": True,
        "marginable": True,
        "shortable": True,
        "easy_to_borrow": True,
        "fractionable": True,
    }
}


@pytest.fixture
def alpaca_assets() -> Dict[str, dict]:
    return ALPCA_ASSETS


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("APCA_API_KEY_ID", "some-made-up-api-key")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "some-made-up-secret-key")
    monkeypatch.setenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
