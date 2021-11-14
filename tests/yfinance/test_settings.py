from pydantic import AnyHttpUrl

from finvestor.yfinance.settings import YFSettings

import pytest


@pytest.mark.disable_auto_env_setup
def test_yahoo_finance_settings_defaults():
    assert YFSettings().dict() == {
        "YAHOO_FINANCE_BASE_URL": AnyHttpUrl(
            "https://query2.finance.yahoo.com",
            scheme="https",
            host="query2.finance.yahoo.com",
            host_type="domain",
        ),
        "YAHOO_FINANCE_SCRAPE_URL": AnyHttpUrl(
            "https://finance.yahoo.com/quote",
            scheme="https",
            host="finance.yahoo.com/quote",
            host_type="domain",
        ),
    }


def test_yahoo_finance_settings_env():
    assert YFSettings().dict() == {
        "YAHOO_FINANCE_BASE_URL": AnyHttpUrl(
            "https://some-overriden-url",
            scheme="https",
            host="some-overriden-url",
            host_type="domain",
        ),
        "YAHOO_FINANCE_SCRAPE_URL": AnyHttpUrl(
            "https://some-other-overriden-url",
            scheme="https",
            host="some-other-overriden-url",
            host_type="domain",
        ),
    }
