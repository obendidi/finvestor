from collections.abc import Iterable
from datetime import datetime, timedelta
from random import random

import numpy as np
import pandas as pd
import pytz

from finvestor.core.timeframe import TimeFrame
from finvestor.data_providers.schemas import Bar, Bars, BarsRequestParams


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


def test_Bars_df_method():
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


def test_BarsRequestParams_data_validation(bars_request_params_test_cases):
    (
        interval,
        period,
        start,
        end,
        kwargs,
        expecation,
    ) = bars_request_params_test_cases
    with expecation:
        BarsRequestParams(
            interval=interval, period=period, start=start, end=end, **kwargs
        )


def test_BarsRequestParams_start_is_not_None_end_is_None():
    start = pytz.utc.localize(datetime.utcnow()) - timedelta(days=5)
    interval = TimeFrame("1d")

    params = BarsRequestParams(start=start, interval=interval)
    assert params.end == start + timedelta(days=1)
