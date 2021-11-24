from typing import Dict, List
from datetime import datetime, timedelta
import pytz
from finvestor.data_providers.utils import (
    ValidInterval,
    ValidPeriod,
    time_period_to_timedelta,
)


class _ValidIntervals:
    _max_days_to_valid_intervals: Dict[float, List[ValidInterval]] = {
        7: ["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"],
        59.9: ["2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"],
        729.9: ["1h", "1d", "5d", "1mo", "3mo"],
    }
    _default: List[ValidInterval] = ["1d", "5d", "1mo", "3mo"]

    @classmethod
    def from_timedelta(cls, delta: timedelta) -> List[ValidInterval]:
        for max_days, valid_intervals in cls._max_days_to_valid_intervals.items():
            if delta.days <= max_days:
                return valid_intervals
        return cls._default

    @classmethod
    def from_period(cls, period: ValidPeriod) -> List[ValidInterval]:
        delta = time_period_to_timedelta(period)
        return cls.from_timedelta(delta)

    @classmethod
    def from_datetime(cls, _datetime: datetime) -> List[ValidInterval]:
        now = pytz.utc.localize(datetime.utcnow())
        delta = now - _datetime
        return cls.from_timedelta(delta)


def get_valid_intervals_for_period(
    interval: ValidInterval, range: ValidPeriod
) -> List[ValidInterval]:
    valid_intervals = _ValidIntervals.from_period(range)
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
    interval: ValidInterval, start: datetime, end: datetime
) -> datetime:

    delta = time_period_to_timedelta(interval)
    if start + delta <= end:
        return end
    return end + delta
