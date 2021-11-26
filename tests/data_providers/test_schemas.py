from collections.abc import Iterable
from datetime import datetime, timedelta
from random import random
from contextlib import nullcontext as does_not_raise

import numpy as np
import pandas as pd
import pytest
import pytz
from pydantic import ValidationError
from finvestor.data_providers.timeframe import TimeFrame
from finvestor.data_providers.schemas import Bar, Bars, GetBarsDataParams
from finvestor.data_providers.utils import pytz_utc_now


def test_Bars_schema_is_iterable():
    bar = Bar(
        timestamp=datetime.now(),
        close=random(),
        high=random(),
        low=random(),
        open=random(),
        volume=random(),
        interval="1m",
    )
    bars = Bars(__root__=[bar])
    assert isinstance(bars, Iterable)
    assert len(bars) == 1
    assert bars[0] == bar


def test_Dars_df_method():
    bar1 = Bar(
        timestamp=datetime.now(),
        close=random(),
        high=random(),
        low=random(),
        open=random(),
        volume=random(),
        interval="1m",
    )
    bar2 = Bar(
        timestamp=datetime.now(),
        close=np.nan,
        high=random(),
        low=random(),
        open=random(),
        volume=np.nan,
        interval="5m",
    )
    bar3 = Bar(
        timestamp=datetime.now(),
        close=np.nan,
        high=np.nan,
        low=np.nan,
        open=np.nan,
        volume=np.nan,
        interval="1h",
    )
    bars = Bars(__root__=[bar1, bar2, bar3])
    df = bars.df()
    assert isinstance(df, pd.DataFrame)
    df_dict = df.to_dict(orient="list")
    assert np.array_equal(
        df_dict["close"], [0.8444218515250481, np.nan], equal_nan=True
    )
    assert np.array_equal(df_dict["high"], [0.7579544029403025, 0.4049341374504143])
    assert np.array_equal(df_dict["low"], [0.420571580830845, 0.7837985890347726])
    assert np.array_equal(df_dict["open"], [0.25891675029296335, 0.30331272607892745])
    assert np.array_equal(
        df_dict["volume"], [0.5112747213686085, np.nan], equal_nan=True
    )
    assert df_dict["interval"] == [TimeFrame("1m"), TimeFrame("5m")]


testdata = [
    pytest.param(
        None,
        None,
        None,
        pytest.raises(
            ValidationError,
            match=(
                r"Please provide either a period or start\[-end\] datetimes\. \(type=value_error\)"  # noqa
            ),
        ),
        id="missing_start_or_period",
    ),
    pytest.param(
        "1d",
        None,
        None,
        pytest.raises(
            ValidationError,
            match=r"No subField provided, Expected <class 'TimeFrame'>, got <class 'str'> \(value=1d\) \(type=type_error\)",  # noqa
        ),
        id="invalid_period_value",
    ),
    pytest.param(
        None,
        "bob",
        None,
        pytest.raises(
            ValidationError,
            match=r"invalid datetime format \(type=value_error.datetime\)",  # noqa
        ),
        id="invalid_start_value",
    ),
    pytest.param(
        TimeFrame("1d"),
        "bob",
        None,
        pytest.raises(
            ValidationError,
            match=r"invalid datetime format \(type=value_error.datetime\)",  # noqa
        ),
        id="invalid_start_value_with_1d_period",
    ),
    pytest.param(
        TimeFrame("1d"),
        pytz_utc_now() - timedelta(days=2),
        None,
        pytest.raises(
            ValidationError,
            match=r"Please provide ONLY one of period or start\[-end\] datetimes",  # noqa
        ),
        id="invalid_start_and_period",
    ),
    pytest.param(
        TimeFrame("1d"),
        None,
        pytz_utc_now(),
        pytest.raises(
            ValidationError,
            match=r"Please provide ONLY one of period or start\[-end\] datetimes",  # noqa
        ),
        id="invalid_end_and_period",
    ),
    pytest.param(
        None,
        datetime.now(),
        None,
        pytest.raises(
            ValidationError,
            match=r"Please provide an UTC start\[-end\] datetimes \(or tz aware\), got: *-*-* *:*:*.* \(type=value_error\)",  # noqa
        ),
        id="invalid_start_not_utc_or_tz_aware",
    ),
    pytest.param(
        None,
        pytz_utc_now() + timedelta(days=5),
        None,
        pytest.raises(
            ValidationError,
            match=r"Provided start is invalid: start<*-*-* *:*:*.*\+00:00> >= now<*-*-* *:*:*.*\+00:00>. \(type=value_error\)",  # noqa
        ),
        id="invalid_start_larger_than_current_time",
    ),
    pytest.param(
        None,
        pytz_utc_now() - timedelta(hours=1),
        pytz_utc_now() - timedelta(hours=2),
        pytest.raises(
            ValidationError,
            match=r"Provided end is invalid: start<*-*-* *:*:*.*\+00:00> >= end<*-*-* *:*:*.*\+00:00>. \(type=value_error\)",  # noqa
        ),
        id="invalid_start_larger_than_end",
    ),
    pytest.param(
        TimeFrame("1d"),
        None,
        None,
        does_not_raise(),
        id="valid_period_1d_str_TimeFrame",
    ),
    pytest.param(
        TimeFrame(timedelta(hours=3)),
        None,
        None,
        does_not_raise(),
        id="valid_period_3h_timedelta_TimeFrame",
    ),
    pytest.param(
        None,
        pytz_utc_now() - timedelta(minutes=5),
        None,
        does_not_raise(),
        id="valid_start_utc_5_min_ago",
    ),
    pytest.param(
        None,
        datetime.now(tz=pytz.timezone("America/New_York")) - timedelta(minutes=5),
        None,
        does_not_raise(),
        id="valid_start_tz_aware_5_min_ago",
    ),
    pytest.param(
        None,
        pytz_utc_now() - timedelta(minutes=5),
        pytz_utc_now(),
        does_not_raise(),
        id="valid_start_end_utc",
    ),
]


@pytest.mark.parametrize("period,start,end,expectation", testdata)
def test_GetBarsDataParams_with_default_interval(period, start, end, expectation):
    with expectation:
        GetBarsDataParams(period=period, start=start, end=end)


@pytest.mark.parametrize(
    "interval,period,start,end,expectation",
    [
        (
            TimeFrame("1d"),
            TimeFrame("1h"),
            None,
            None,
            pytest.raises(
                ValidationError,
                match=r"Interval=TimeFrame\(timeperiod='1d'\) is larger than provided period=TimeFrame\(timeperiod='1h'\) \(type=value_error\)",  # noqa
            ),
        ),
        (
            TimeFrame("1d"),
            None,
            pytz_utc_now() - timedelta(minutes=5),
            pytz_utc_now() - timedelta(minutes=2),
            pytest.raises(
                ValidationError,
                match=r"Interval=TimeFrame\(timeperiod='1d'\) is larger than diff between start-end",  # noqa
            ),
        ),
    ],
)
def test_GetBarsDataParams_with_custom_interval(
    interval, period, start, end, expectation
):
    with expectation:
        GetBarsDataParams(period=period, start=start, end=end, interval=interval)
