import pytest

from finvestor.yfinance.settings import YFSettings


@pytest.mark.disable_auto_env_setup
def test_yahoo_finance_settings_defaults(snapshot):
    assert YFSettings() == snapshot


def test_yahoo_finance_settings_env(snapshot):
    assert YFSettings() == snapshot
