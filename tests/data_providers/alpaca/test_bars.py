from datetime import datetime, timedelta

import pytest
import pytz

from finvestor.core.timeframe import TimeFrame
from finvestor.data_providers.alpaca.bars import AlpacaBarsRequestParams


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


# _START = datetime(year=2021, month=11, day=26, hour=15, tzinfo=pytz.utc)


# @pytest.mark.parametrize(
#     "ticker,ticker_type,request_params,expectation",
#     [
#         pytest.param(
#             "TSLA",
#             "stock",
#             {"start": _START, "end": _START + timedelta(minutes=2), "interval": "1Min"},
#             does_not_raise(),
#             id="bars-TSLA-stock-dict-params",
#         ),
#         pytest.param(
#             "TSLA",
#             "stock",
#             BarsRequestParams(
#                 start=_START,
#                 end=_START + timedelta(minutes=1),
#                 interval=TimeFrame("1Min"),
#             ),
#             does_not_raise(),
#             id="bars-TSLA-stock-BarsRequestParams",
#         ),
#         pytest.param(
#             "TSLA",
#             "stock",
#             {
#                 "start": _START,
#                 "end": _START + timedelta(minutes=5),
#                 "interval": "1Min",
#                 "limit": 2,
#             },
#             does_not_raise(),
#             id="bars-TSLA-stock-limit-2",
#         ),
#         pytest.param(
#             "BTCUSD",
#             "crypto",
#             {"start": _START, "end": _START + timedelta(minutes=2), "interval": "1Min"},
#             does_not_raise(),
#             id="bars-BTCUSD-crypto",
#         ),
#         pytest.param(
#             "ADAUSD",  # ADA not supported at times of writing on alpaca
#             "crypto",
#             {"start": _START, "end": _START + timedelta(minutes=2), "interval": "1Min"},
#             pytest.raises(EmptyBars),
#             id="bars-ADAUSD-crypto",
#         ),
#         pytest.param(
#             "TSLA",  # market is closed on a Sunday so empty bar
#             "stock",
#             {
#                 "start": datetime(
#                     year=2021, month=11, day=28, hour=15, tzinfo=pytz.utc
#                 ),
#                 "end": datetime(year=2021, month=11, day=28, hour=16, tzinfo=pytz.utc),
#                 "interval": "1Min",
#             },
#             pytest.raises(EmptyBars),
#             id="bars-TSLA-stock-weekend",
#         ),
#     ],
# )
# @pytest.mark.vcr
# async def test_get_alpaca_bars(
#     snapshot, async_client, ticker, ticker_type, request_params, expectation
# ):
#     with expectation:
#         bars = await get_alpaca_bars(
#             ticker,
#             request_params,
#             historical_data_delay=timedelta(0),
#             client=async_client,
#             ticker_type=ticker_type,
#         )
#         assert bars == snapshot
