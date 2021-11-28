from datetime import timedelta

import pytest
from pydantic.errors import DurationError

from finvestor.data_providers.utils import (
    _NUM_DAYS_IN_A_MONTH,
    _NUM_DAYS_IN_A_YEAR,
    get_closest_value_to_timedelta,
    parse_duration,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        (timedelta(days=1), timedelta(days=1)),
        (5, timedelta(seconds=5)),
        (0.5, timedelta(seconds=0.5)),
        ("P3DT12H30M5S", timedelta(days=3, seconds=45005)),
        ("P3DT12H30M5S".encode(), timedelta(days=3, seconds=45005)),
        ("32s", timedelta(seconds=32)),
        ("15m", timedelta(minutes=15)),
        ("1m 10s", timedelta(minutes=1, seconds=10)),
        ("1M59S", timedelta(minutes=1, seconds=59)),
        ("mtd", timedelta(days=_NUM_DAYS_IN_A_MONTH)),
        ("ytd", timedelta(days=_NUM_DAYS_IN_A_YEAR)),
        (
            "1month 3weeks 5days 23minutes",
            timedelta(days=_NUM_DAYS_IN_A_MONTH + 21 + 5, minutes=23),
        ),
        ("1y 3.5mo", timedelta(days=_NUM_DAYS_IN_A_YEAR + _NUM_DAYS_IN_A_MONTH * 3.5)),
        # ALPCA timeframes
        ("1Min", timedelta(minutes=1)),
        ("15Min", timedelta(minutes=15)),
        ("1Hour", timedelta(hours=1)),
        ("3Hour", timedelta(hours=3)),
        ("1Day", timedelta(days=1)),
    ],
)
def test_parse_duration(value, expected):
    assert parse_duration(value) == expected


def test_parse_duration_error_only_chars():
    with pytest.raises(DurationError):
        parse_duration("mlmm")


def test_parse_duration_error_invalid_unit():
    with pytest.raises(DurationError):
        parse_duration("157q")


@pytest.mark.parametrize(
    "key,expected",
    [
        (timedelta(minutes=1), "1Minutes"),
        (timedelta(minutes=1, seconds=20), "1Minutes"),
        (timedelta(minutes=1, seconds=50), "2m"),
        (timedelta(days=1, seconds=50), "2h"),
        (timedelta(days=4), "5d"),
    ],
)
def test_get_closest_value_to_timedelta(key, expected):
    data = {
        timedelta(minutes=1): "1Minutes",
        timedelta(minutes=2): "2m",
        timedelta(minutes=5): "5Minutes",
        timedelta(minutes=30): "30Min",
        timedelta(hours=2): "2h",
        timedelta(days=5): "5d",
    }

    assert get_closest_value_to_timedelta(data, key) == expected


# @pytest.mark.parametrize(
#     "interval,expected",
#     [
#         ("1m", "1d"),
#         ("30m", "1d"),
#         ("1h", "1d"),
#         ("5d", "1mo"),
#         ("1mo", "6mo"),
#         ("3mo", "6mo"),
#     ],
# )
# def test_get_smallest_valid_period_for_interval(interval, expected):
#     assert get_smallest_valid_period_for_interval(interval) == expected


# @pytest.mark.parametrize(
#     "period,expected",
#     [
#         ("15m", timedelta(minutes=15)),
#         ("1h", timedelta(hours=1)),
#         ("7d", timedelta(days=7)),
#         ("3mo", timedelta(days=3 * 30.417)),
#         ("3y", timedelta(days=3 * 365)),
#     ],
# )
# def test_time_period_to_timedelta(period, expected):
#     assert time_period_to_timedelta(period) == expected


# def test_time_period_to_timedelta_value_error():
#     with pytest.raises(ValueError):
#         time_period_to_timedelta("max")


# def test_default_interval_type():
#     value = DefaultIntervalType("1m")
#     assert isinstance(DEFAULT_INTERVAL, DefaultIntervalType)
#     assert value == "1m"


# def test_default_interval_type_with_invalid_interval():
#     with pytest.raises(ValidationError):
#         DefaultIntervalType.validate("6h")
