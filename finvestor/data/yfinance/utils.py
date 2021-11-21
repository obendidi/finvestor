import logging
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Union

import pytz

from finvestor.models import ValidInterval

logger = logging.getLogger(__name__)

ValidRange = Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
]


INTERVAL_TO_MAX_DAYS: Dict[ValidInterval, float] = {
    "1m": 7,
    "2m": 59.9,
    "5m": 59.9,
    "15m": 59.9,
    "30m": 59.9,
    "1h": 729.9,
}


class _ValidIntervals:
    _max_days_to_valid_intervals: Dict[float, List[ValidInterval]] = {
        7: ["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"],
        59.9: ["2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"],
        729.9: ["1h", "1d", "5d", "1mo", "3mo"],
    }
    _default: List[ValidInterval] = ["1d", "5d", "1mo", "3mo"]

    @classmethod
    def from_range(cls, range: ValidRange) -> List[ValidInterval]:
        delta = time_symbol_to_timedelta(range)
        for max_days, valid_intervals in cls._max_days_to_valid_intervals.items():
            if delta.days <= max_days:
                return valid_intervals
        return cls._default

    @classmethod
    def from_datetime(cls, _datetime: datetime) -> List[ValidInterval]:
        now = pytz.utc.localize(datetime.utcnow())
        delta = now - _datetime
        for max_days, valid_intervals in cls._max_days_to_valid_intervals.items():
            if delta.days <= max_days:
                return valid_intervals
        return cls._default


def time_symbol_to_timedelta(symbol: Union[ValidInterval, ValidRange]) -> timedelta:
    if symbol.endswith("m"):
        return timedelta(minutes=float(symbol[:-1]))
    elif symbol.endswith("h"):
        return timedelta(hours=1)
    elif symbol.endswith("d"):
        return timedelta(days=float(symbol[:-1]))
    elif symbol.endswith("mo"):
        return timedelta(days=float(symbol[:-2]) * 30.417)
    elif symbol.endswith("y"):
        return timedelta(days=float(symbol[:-1]) * 365)
    elif symbol == "ytd":
        return timedelta(days=365)
    elif symbol == "max":
        return timedelta(days=365 * 10)

    raise ValueError(f"Unsupported symbol: {symbol}")


def get_valid_intervals_for_range(
    interval: ValidInterval, range: ValidRange
) -> List[ValidInterval]:
    valid_intervals = _ValidIntervals.from_range(range)
    if interval in valid_intervals:
        idx = valid_intervals.index(interval)
        return valid_intervals[idx:]
    return valid_intervals


def get_valid_intervals_for_datetime(
    interval: ValidInterval, _datetime: datetime
) -> List[ValidInterval]:
    valid_intervals = _ValidIntervals.from_datetime(_datetime)
    if interval in valid_intervals:
        idx = valid_intervals.index(interval)
        return valid_intervals[idx:]
    return valid_intervals


def coerce_end_time_to_interval(
    ticker: str, interval: ValidInterval, start_date: datetime, end_date: datetime
) -> datetime:

    delta = time_symbol_to_timedelta(interval)

    if start_date + delta < end_date:
        return end_date

    logger.debug(
        f"[{ticker}]: Interval={interval} is too big for provided start={start_date} "  # type: ignore # noqa
        f"-> end={end_date}, updating end_date to {start_date + delta}"
    )
    return start_date + delta
