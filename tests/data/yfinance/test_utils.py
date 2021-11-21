from datetime import datetime, timedelta

import pytest
import pytz

from finvestor.data.yfinance.utils import (
    get_valid_intervals_for_datetime,
    get_valid_intervals_for_range,
    time_symbol_to_timedelta,
)


@pytest.mark.parametrize(
    "symbol,expected",
    [
        ("15m", timedelta(minutes=15)),
        ("1h", timedelta(hours=1)),
        ("7d", timedelta(days=7)),
        ("5y", timedelta(days=5 * 365)),
    ],
)
def test_time_symbol_to_timedelta(symbol, expected):
    assert time_symbol_to_timedelta(symbol) == expected


def test_time_symbol_to_timedelta_value_error():
    with pytest.raises(ValueError):
        time_symbol_to_timedelta("lol")


@pytest.mark.parametrize(
    "interval,range,expected",
    [
        ("1m", "1d", ["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"]),
        ("1h", "5d", ["1h", "1d", "5d", "1mo", "3mo"]),
        ("1m", "6mo", ["1h", "1d", "5d", "1mo", "3mo"]),
    ],
)
def test_get_valid_intervals_for_range(interval, range, expected):
    assert get_valid_intervals_for_range(interval, range) == expected


@pytest.mark.parametrize(
    "interval,_datetime,expected",
    [
        (
            "1m",
            pytz.utc.localize(datetime.utcnow()) - timedelta(days=1),
            ["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"],
        ),
        (
            "1h",
            pytz.utc.localize(datetime.utcnow()) - timedelta(days=5),
            ["1h", "1d", "5d", "1mo", "3mo"],
        ),
        (
            "1m",
            pytz.utc.localize(datetime.utcnow()) - timedelta(days=180),
            ["1h", "1d", "5d", "1mo", "3mo"],
        ),
    ],
)
def test_get_valid_intervals_for_datetime(interval, _datetime, expected):
    assert get_valid_intervals_for_datetime(interval, _datetime) == expected
