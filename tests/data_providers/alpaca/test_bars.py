from contextlib import nullcontext as does_not_raise
from datetime import datetime, timedelta

import pytest
import pytz

from finvestor.data_providers.alpaca.bars import (
    AlpacaBarsRequestParams,
    get_alpaca_bars,
)
from finvestor.data_providers.exceptions import EmptyBars
from finvestor.data_providers.timeframe import TimeFrame


def test_AlpacaBarsRequestParams_data_validation(alpaca_bars_request_params_test_cases):
    (
        interval,
        period,
        start,
        end,
        kwargs,
        expecation,
    ) = alpaca_bars_request_params_test_cases
    with expecation:
        AlpacaBarsRequestParams(
            interval=interval, period=period, start=start, end=end, **kwargs
        )


@pytest.mark.parametrize(
    "period,historical_data_delay",
    [
        ("1d 10m", timedelta(minutes=15)),
        ("1Min", timedelta(minutes=1)),
        ("25Min", timedelta(minutes=100)),
    ],
)
def test_AlpacaBarsRequestParams_convert_period_to_start_end(
    period, historical_data_delay
):

    params = AlpacaBarsRequestParams(
        period=period, historical_data_delay=historical_data_delay
    )

    now = datetime.now(tz=pytz.UTC)
    assert params.period.duration == period
    assert TimeFrame(params.end - params.start) == params.period
    # not that accurate of a test, but good enough
    assert now - params.end > historical_data_delay


@pytest.mark.parametrize(
    "interval,expected",
    [
        ("1Min", "1Min"),
        ("2m", "2Min"),
        ("25Min", "30Min"),
        ("1d", "1Day"),
        (timedelta(days=1, hours=2), "1Day"),
    ],
)
def test_AlpacaBarsRequestParams_convert_interval(interval, expected):

    period = "5d"
    params = AlpacaBarsRequestParams(period=period, interval=interval)
    assert params.interval.duration == expected


@pytest.mark.parametrize(
    "ticker_type,kwargs",
    [("stock", {"adjustment": "all"}), ("crypto", {})],
)
def test_AlpacaBarsRequestParams___call___(ticker_type, kwargs):
    start = datetime.now(tz=pytz.UTC) - timedelta(days=6)
    end = start + timedelta(days=5)
    req_params = AlpacaBarsRequestParams(start=start, end=end, interval="1Day")

    assert req_params(ticker_type=ticker_type) == {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "limit": 10000,
        "timeframe": "1Day",
        **kwargs,
    }


@pytest.mark.parametrize(
    "ticker,start,end,ticker_type,limit,expectation",
    [
        pytest.param(
            "TSLA",
            datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc),
            datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc)
            + timedelta(minutes=5),
            "stock",
            10000,
            does_not_raise(),
            id="TSLA-stock-2021-11-26T15-00-00",
        ),
        pytest.param(
            "TSLA",
            datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc),
            datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc)
            + timedelta(minutes=5),
            "stock",
            2,
            does_not_raise(),
            id="TSLA-stock-2021-11-26T15-00-00-limit-2",
        ),
        pytest.param(
            "BTCUSD",
            datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc),
            datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc)
            + timedelta(minutes=5),
            "crypto",
            10000,
            does_not_raise(),
            id="BTCUSD-crypto-2021-11-26T15-00-00",
        ),
        pytest.param(
            "ADAUSD",  # ADA not supported at times of writing on alpaca
            datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc),
            datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc)
            + timedelta(minutes=5),
            "crypto",
            10000,
            pytest.raises(EmptyBars),
            id="ADAUSD-crypto-2021-11-26T15-00-00",
        ),
        pytest.param(
            "TSLA",  # market is closed on a sunday so empty bar
            datetime(year=2021, month=11, day=28, hour=15, tzinfo=pytz.utc),
            datetime(year=2021, month=11, day=28, hour=15, tzinfo=pytz.utc)
            + timedelta(minutes=5),
            "stock",
            10000,
            pytest.raises(EmptyBars),
            id="TSLA-stock-2021-11-28T15-00-00",
        ),
    ],
)
@pytest.mark.vcr
async def test_get_alpaca_bars(
    snapshot, async_client, ticker, start, end, ticker_type, limit, expectation
):
    request_params = {"start": start, "end": end, "interval": "1Min", "limit": limit}
    with expectation:
        bars = await get_alpaca_bars(
            ticker,
            request_params,
            historical_data_delay=timedelta(0),
            client=async_client,
            ticker_type=ticker_type,
        )
        assert bars == snapshot
