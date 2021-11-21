from datetime import datetime, timedelta

import pytest
import pytz

from finvestor.data.yfinance.bars import get_quotes


class MockAsyncClient:
    def __init__(self):
        pass

    async def get(self, url, *, params):
        pass


@pytest.mark.parametrize(
    "start,end",
    [
        (datetime.now(), None),
        (pytz.utc.localize(datetime.utcnow()), datetime.now()),
        (
            pytz.utc.localize(datetime.utcnow()) + timedelta(days=2),
            pytz.utc.localize(datetime.utcnow()),
        ),
    ],
)
async def test_get_quotes_invalid_start_end_times(anyio_backend, start, end):
    client = MockAsyncClient()
    with pytest.raises(AssertionError):
        await get_quotes("TSLA", client=client, start=start, end=end, range=None)
