import re
import typing as tp
from datetime import timedelta

import attr
from pydantic import ValidationError
from pydantic.datetime_parse import parse_duration as parse_duration_pydantic
from pydantic.errors import DurationError
from pydantic.fields import ModelField

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


def parse_duration(value: tp.Any) -> timedelta:
    try:
        return parse_duration_pydantic(value)
    except DurationError:
        pass

    if value.lower() == "mtd":
        return timedelta(days=_NUM_DAYS_IN_A_MONTH)
    if value.lower() == "ytd":
        return timedelta(days=_NUM_DAYS_IN_A_YEAR)

    kwargs: tp.Dict[str, float] = {}
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


TimeFrameType = tp.TypeVar("TimeFrameType")


@attr.s
class TimeFrame(tp.Generic[TimeFrameType]):

    duration = attr.ib(eq=parse_duration, order=parse_duration)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: tp.Any, field: ModelField):
        if not field.sub_fields:
            if not isinstance(value, cls):
                raise TypeError(
                    f"No subField provided, Expected <class '{cls.__name__}'>, "
                    f"got {type(value)} (value={value})"
                )
            return value

        sub_field = field.sub_fields[0]

        if not isinstance(value, cls):
            value = cls(value)

        _, error = sub_field.validate(value.duration, {}, loc="duration")
        if error:
            raise ValidationError([error], cls)  # type: ignore
        return value
