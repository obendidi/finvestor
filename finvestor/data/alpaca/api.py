from datetime import datetime, timedelta
from typing import Optional

from alpaca_trade_api.rest import REST, TimeFrame


class AlpacaClient:
    _client: REST = None

    def __init__(self):
        if self._client is None:
            AlpacaClient._client = REST()

    def __getattr__(self, *args):
        return self._client.__getattribute__(*args)

    def get_ticker_price(self, ticker: str, date_time: Optional[datetime] = None):
        """Get a ticker price either at a specific datetime or latest.

        The maximum granularity that we can get at the free tier is 1 minute bars,

        Args:
            ticker: Symbol of the ticker to get
            date_time: Timezone aware datetime. Defaults to None.

        Returns:
            float: Blatest price or closest price to date_time
        """

        if date_time is None:
            bar = self._client.get_latest_bar(ticker)
            return bar
        start_date = date_time.replace(second=0)
        end_date = (date_time + timedelta(minutes=1)).replace(second=0)
        bars = self._client.get_bars(
            ticker,
            TimeFrame.Minute,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
        )
        return bars
