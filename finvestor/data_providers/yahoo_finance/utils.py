import typing as tp
from datetime import datetime

import pytz

from finvestor.core.timeframe import parse_duration
from finvestor.data_providers.schemas import VALID_INTERVALS, ValidInterval, ValidPeriod

YF_MAX_DAYS_TO_VALID_INTERVALS: tp.Dict[float, tp.Tuple[ValidInterval, ...]] = {
    7: VALID_INTERVALS,  # all
    59.9: VALID_INTERVALS[1:],  # 2m and above
    729.9: VALID_INTERVALS[5:],  # 1h and above
}
# by default smallest always valid is 1d
YF_DEFAULT_VALID_INTERVALS: tp.Tuple[ValidInterval, ...] = VALID_INTERVALS[6:]


def get_valid_intervals(
    period: tp.Optional[ValidPeriod] = None,
    start: tp.Optional[datetime] = None,
    **kwargs: tp.Any,
) -> tp.Tuple[ValidInterval, ...]:
    if period is not None:
        delta = parse_duration(period)
    elif start is not None:
        delta = datetime.now(tz=pytz.UTC) - start
    else:
        raise NotImplementedError(f"Missing value: period={period} | start={start}")

    for max_days, valid_intervals in YF_MAX_DAYS_TO_VALID_INTERVALS.items():
        if delta.days <= max_days:
            return valid_intervals
    return YF_DEFAULT_VALID_INTERVALS


def get_smallest_valid_interval(
    period: tp.Optional[ValidPeriod] = None,
    start: tp.Optional[datetime] = None,
    **kwargs: tp.Any,
) -> ValidInterval:
    return get_valid_intervals(period=period, start=start)[0]
