import logging
from datetime import timedelta, datetime
from typing import Any, Dict
from pydantic.datetime_parse import (
    parse_duration as parse_duration_pydantic,
)
from pydantic.errors import DurationError
import pytz
import re

logger = logging.getLogger(__name__)


_NUM_DAYS_IN_A_MONTH = 30.417
_NUM_DAYS_IN_A_YEAR = 365
_UNITS_REGEX = r"(?P<val>\d+(\.\d+)?)(?P<unit>(mo|s|m|h|d|w|y)?)"
_UNITS = {
    "s": "seconds",
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks",
}


def parse_duration(value: Any) -> timedelta:
    try:
        return parse_duration_pydantic(value)
    except DurationError:
        pass

    if value.lower() == "mtd":
        return timedelta(days=_NUM_DAYS_IN_A_MONTH)
    if value.lower() == "ytd":
        return timedelta(days=_NUM_DAYS_IN_A_YEAR)

    kwargs: Dict[str, float] = {}
    for match in re.finditer(_UNITS_REGEX, value, flags=re.I):
        unit = match.group("unit").lower()
        val = float(match.group("val"))
        if unit == "mo":
            unit = "d"
            val = val * _NUM_DAYS_IN_A_MONTH
        elif unit == "y":
            unit = "d"
            val = val * _NUM_DAYS_IN_A_YEAR
        if unit not in _UNITS:
            raise DurationError()
        if _UNITS[unit] in kwargs:
            kwargs[_UNITS[unit]] += val
        else:
            kwargs[_UNITS[unit]] = val

    if not kwargs:
        raise DurationError()
    return timedelta(**kwargs)  # type: ignore


def pytz_utc_now() -> datetime:
    return pytz.utc.localize(datetime.utcnow())


# def get_smallest_valid_period_for_interval(interval: ValidInterval) -> ValidPeriod:
#     if interval.endswith("m") or interval.endswith("h"):
#         return "1d"
#     elif interval.endswith("d"):
#         return "1mo"
#     return "6mo"


# def validate_start_end_period_args(
#     period: Optional[ValidPeriod] = None,
#     start: Optional[datetime] = None,
#     end: Optional[datetime] = None,
# ) -> Union[Tuple[ValidPeriod, None, None], Tuple[None, datetime, datetime]]:
#     if period is None and start is None:
#         raise ValueError("Please provide either a range or start[-end] datetimes.")

#     if period is not None and start is not None:
#         logger.warning(
#             f"Period={period} and start={start} were provided, "
#             f"giving priority to period={period}"
#         )

#     if period is not None:
#         return period, None, None

#     # the if is uncessary, it's just there to please mypy
#     if start is not None:
#         now = pytz.utc.localize(datetime.utcnow())
#         if start.tzinfo != pytz.utc:
#             raise ValueError(
#                 f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
#                 f"got: start<{start.tzinfo}>"
#             )
#         if start >= now:
#             raise ValueError(
#                 f"Provided start datetime ({start}) should be larger than now "
#                 f"datetime ({now})"
#             )
#         if end is not None:
#             if end.tzinfo != pytz.utc:
#                 raise ValueError(
#                     f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
#                     f"got: end<{end.tzinfo}>"
#                 )
#             if end < start:
#                 raise ValueError(
#                     f"Provided end datetime ({end}) should be larger than start "
#                     f"datetime ({start})"
#                 )
#         else:
#             end = now
#         return None, start, end
#     raise NotImplementedError()


# @attr.s
# class TimeFrame:
#     _INTERVALS = ["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"]
#     _PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd"]
#     timeframe: _ValidInterval = attr.ib(
#         eq=time_period_to_timedelta, order=time_period_to_timedelta
#     )


# if __name__ == "__main__":
#     in1 = TimeFrame("2m")
#     in2 = TimeFrame(timedelta(minutes=2))
#     print(in1)
#     print(in2)
#     print(in1 == in2)
#     print(in1 >= in2)
