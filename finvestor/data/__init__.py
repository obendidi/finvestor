from finvestor.core import config

if config.DATA_PROVIDER == "yfinance":
    from finvestor.data.yfinance.bars import (
        get_bar_at_timestamp,
        get_bars,
        get_closest_price_at_timestamp,
        get_latest_bar,
    )
    from finvestor.data.yfinance.scrapper import get_asset
else:  # alpaca
    raise Exception()
