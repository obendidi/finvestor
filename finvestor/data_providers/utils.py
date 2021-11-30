import logging
import typing as tp
from datetime import datetime, timedelta
from itertools import islice

from sortedcontainers import SortedDict

from finvestor.core.timeframe import parse_duration
from finvestor.data_providers.schemas import Bar, ValidInterval, ValidPeriod

logger = logging.getLogger(__name__)


def get_closest_value_to_timedelta(
    data_dict: tp.Mapping[timedelta, tp.Any], key: timedelta
) -> tp.Any:
    sorted_dict = SortedDict(data_dict)
    keys = list(islice(sorted_dict.irange(minimum=key), 1))
    keys.extend(islice(sorted_dict.irange(maximum=key, reverse=True), 1))
    closest_key = min(keys, key=lambda k: abs(key - k))
    return data_dict[closest_key]


def get_smallest_valid_period_for_interval(interval: ValidInterval) -> ValidPeriod:
    duration = parse_duration(interval)
    if duration.days < 1:
        return "1d"
    elif duration.days < 5:
        return "5d"
    elif interval == "1mo":
        return "3mo"
    return "6mo"


def get_closest_price_to_timestamp_from_bar(bar: Bar, timestamp: datetime) -> float:
    bar_open_date = bar.timestamp
    bar_close_date = bar_open_date + parse_duration(bar.interval)
    open_delta = timestamp - bar_open_date
    close_delta = bar_close_date - timestamp
    if open_delta < close_delta:
        return bar.open
    return bar.close


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
#                     f"Only timezone aware datetimes with tz={pytz.UTC} are supported,"
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
