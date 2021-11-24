import logging
from datetime import datetime, timedelta
from typing import Literal, Optional, Tuple, Union

import pytz

logger = logging.getLogger(__name__)

ValidInterval = Literal["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"]
ValidPeriod = Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
]


def time_period_to_timedelta(period: Union[ValidInterval, ValidPeriod]) -> timedelta:
    """Convert a string time period to a timedelta.

    Supports all time periods in ValidInterval and ValidPeriod

    Args:
        period: a supported string period.

    Raises:
        ValueError: if period symbol not supported

    Returns:
        timedelta
    """
    if period.endswith("m"):
        return timedelta(minutes=float(period[:-1]))
    elif period.endswith("h"):
        return timedelta(hours=1)
    elif period.endswith("d"):
        return timedelta(days=float(period[:-1]))
    elif period.endswith("mo"):
        return timedelta(days=float(period[:-2]) * 30.417)
    elif period.endswith("y"):
        return timedelta(days=float(period[:-1]) * 365)
    elif period == "ytd":
        return timedelta(days=365)
    elif period == "max":
        return timedelta(days=365 * 10)

    raise ValueError(f"Unsupported period: {period}")


def get_valid_period_for_interval(interval: ValidInterval) -> ValidPeriod:
    if interval.endswith("m") or interval.endswith("h"):
        return "1d"
    elif interval.endswith("d"):
        return "1mo"
    return "6mo"


def validate_start_end_period_args(
    period: Optional[ValidPeriod] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Union[Tuple[ValidPeriod, None, None], Tuple[None, datetime, datetime]]:
    if period is None and start is None:
        raise ValueError("Please provide either a range or start[-end] datetimes.")

    if period is not None and start is not None:
        logger.warning(
            f"Period={period} and start={start} were provided, "
            f"giving priority to period={period}"
        )

    if period is not None:
        return period, None, None

    # the if is uncessary, it's just there to please mypy
    if start is not None:
        now = pytz.utc.localize(datetime.utcnow())
        if start.tzinfo != pytz.utc:
            raise ValueError(
                f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
                f"got: start<{start.tzinfo}>"
            )
        if start >= now:
            raise ValueError(
                f"Provided start datetime ({start}) should be larger than now "
                f"datetime ({now})"
            )
        if end is not None:
            if end.tzinfo != pytz.utc:
                raise ValueError(
                    f"Only timezone aware datetimes with tz={pytz.UTC} are supported, "
                    f"got: end<{end.tzinfo}>"
                )
            if end <= start:
                raise ValueError(
                    f"Provided end datetime ({end}) should be larger than start "
                    f"datetime ({start})"
                )
        else:
            end = now
        return None, start, end
    raise NotImplementedError()
