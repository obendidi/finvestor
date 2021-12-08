from contextlib import nullcontext as does_not_raise
from datetime import datetime, timedelta

import pytest
import pytz
from pydantic import ValidationError
from pytest_cases import fixture

from finvestor.core.timeframe import TimeFrame

bars_request_params_test_data = [
    pytest.param(
        timedelta(minutes=1),
        None,
        None,
        None,
        {},
        pytest.raises(
            ValidationError,
            match=(
                r"Please provide either a period or start\[-end\] datetimes\. \(type=value_error\)"  # noqa
            ),
        ),
        id="missing_start_or_period",
    ),
    pytest.param(
        timedelta(minutes=1),
        None,
        "bob",
        None,
        {},
        pytest.raises(
            ValidationError,
            match=r"invalid datetime format \(type=value_error.datetime\)",  # noqa
        ),
        id="invalid_start_value",
    ),
    pytest.param(
        timedelta(minutes=1),
        "1d",
        "bob",
        None,
        {},
        pytest.raises(
            ValidationError,
            match=r"invalid datetime format \(type=value_error.datetime\)",  # noqa
        ),
        id="invalid_start_value_with_1d_period",
    ),
    pytest.param(
        timedelta(minutes=1),
        "1d",
        pytz.utc.localize(datetime.utcnow()) - timedelta(days=2),
        None,
        {},
        pytest.raises(
            ValidationError,
            match=r"Please provide ONLY one of period or start\[-end\] datetimes",  # noqa
        ),
        id="invalid_start_and_period",
    ),
    pytest.param(
        timedelta(minutes=1),
        "1d",
        None,
        pytz.utc.localize(datetime.utcnow()),
        {},
        pytest.raises(
            ValidationError,
            match=r"Please provide ONLY one of period or start\[-end\] datetimes",  # noqa
        ),
        id="invalid_end_and_period",
    ),
    pytest.param(
        timedelta(minutes=1),
        None,
        datetime.now(),
        None,
        {},
        pytest.raises(
            ValidationError,
            match=r"Please provide an UTC start\[-end\] datetimes \(or tz aware\), got: *-*-* *:*:*.* \(type=value_error\)",  # noqa
        ),
        id="invalid_start_not_utc_or_tz_aware",
    ),
    pytest.param(
        timedelta(minutes=1),
        None,
        pytz.utc.localize(datetime.utcnow()) + timedelta(days=5),
        None,
        {},
        pytest.raises(
            ValidationError,
            match=r"Provided start is invalid: start<*-*-* *:*:*.*\+00:00> >= now<*-*-* *:*:*.*\+00:00>. \(type=value_error\)",  # noqa
        ),
        id="invalid_start_larger_than_current_time",
    ),
    pytest.param(
        timedelta(minutes=1),
        None,
        pytz.utc.localize(datetime.utcnow()) - timedelta(hours=1),
        pytz.utc.localize(datetime.utcnow()) - timedelta(hours=2),
        {},
        pytest.raises(
            ValidationError,
            match=r"Provided end is invalid: start<*-*-* *:*:*.*\+00:00> >= end<*-*-* *:*:*.*\+00:00>. \(type=value_error\)",  # noqa
        ),
        id="invalid_start_larger_than_end",
    ),
    pytest.param(
        TimeFrame("1d"),
        TimeFrame("1h"),
        None,
        None,
        {},
        pytest.raises(
            ValidationError,
            match=r"Interval=TimeFrame\(duration='(1d|1Day)'\) is larger than provided period=TimeFrame\(duration='1h'\) \(type=value_error\)",  # noqa
        ),
        id="invalid_interval_larger_than_period",
    ),
    pytest.param(
        TimeFrame("1d"),
        None,
        pytz.utc.localize(datetime.utcnow()) - timedelta(minutes=5),
        pytz.utc.localize(datetime.utcnow()) - timedelta(minutes=2),
        {},
        pytest.raises(
            ValidationError,
            match=r"Interval=TimeFrame\(duration='(1d|1Day)'\) is larger than diff between start-end",  # noqa
        ),
        id="invalid_interval_larger_end-start",
    ),
    pytest.param(
        TimeFrame(timedelta(minutes=1)),
        TimeFrame("1d"),
        None,
        None,
        {},
        does_not_raise(),
        id="valid_period_1d_str_TimeFrame",
    ),
    pytest.param(
        TimeFrame(timedelta(minutes=1)),
        TimeFrame(timedelta(hours=3)),
        None,
        None,
        {},
        does_not_raise(),
        id="valid_period_3h_timedelta_TimeFrame",
    ),
    pytest.param(
        TimeFrame(timedelta(minutes=1)),
        None,
        pytz.utc.localize(datetime.utcnow()) - timedelta(minutes=5),
        None,
        {},
        does_not_raise(),
        id="valid_start_utc_5_min_ago",
    ),
    pytest.param(
        TimeFrame(timedelta(minutes=1)),
        None,
        datetime.now(tz=pytz.UTC) - timedelta(minutes=5),
        None,
        {},
        does_not_raise(),
        id="valid_start_utc_5_min_ago_2",
    ),
    pytest.param(
        TimeFrame(timedelta(minutes=1)),
        None,
        datetime.now(tz=pytz.timezone("America/New_York")) - timedelta(minutes=5),
        None,
        {},
        does_not_raise(),
        id="valid_start_tz_aware_5_min_ago",
    ),
    pytest.param(
        TimeFrame(timedelta(minutes=1)),
        None,
        pytz.utc.localize(datetime.utcnow()) - timedelta(minutes=5),
        pytz.utc.localize(datetime.utcnow()),
        {},
        does_not_raise(),
        id="valid_start_end_utc",
    ),
]


@fixture(scope="session")
@pytest.mark.parametrize(
    "interval,period,start,end,kwargs,expectation", bars_request_params_test_data
)
def bars_request_params_test_cases(interval, period, start, end, kwargs, expectation):
    return interval, period, start, end, kwargs, expectation


alpaca_bars_request_params_test_data = bars_request_params_test_data + [
    pytest.param(
        TimeFrame(timedelta(minutes=1)),
        None,
        pytz.utc.localize(datetime.utcnow()) - timedelta(minutes=5),
        pytz.utc.localize(datetime.utcnow()),
        {"historical_data_delay": timedelta(minutes=30)},
        pytest.raises(
            ValidationError,
            match=(
                r"Provided 'end' value does not respect ALPACA historical data delay,"  # noqa
            ),
        ),
        id="end_value_does_not_validate_historical_delay",
    ),
    pytest.param(
        TimeFrame(timedelta(minutes=1)),
        None,
        pytz.utc.localize(datetime.utcnow()) - timedelta(minutes=15),
        pytz.utc.localize(datetime.utcnow()) - timedelta(minutes=5),
        {"historical_data_delay": timedelta(minutes=2)},
        does_not_raise(),
        id="end_value_does_validate_historical_delay",
    ),
]


@fixture(scope="session")
@pytest.mark.parametrize(
    "interval,period,start,end,kwargs,expectation", alpaca_bars_request_params_test_data
)
def alpaca_bars_request_params_test_cases(
    interval, period, start, end, kwargs, expectation
):
    return interval, period, start, end, kwargs, expectation
