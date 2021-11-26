import attr
from pydantic.fields import ModelField
from pydantic import ValidationError

from typing import Any, TypeVar, Generic


from finvestor.data_providers.utils import parse_duration


TimeFrameType = TypeVar("TimeFrameType")


@attr.s
class TimeFrame(Generic[TimeFrameType]):

    timeperiod = attr.ib(eq=parse_duration, order=parse_duration)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, field: ModelField):
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

        _, error = sub_field.validate(value.timeperiod, {}, loc="timeperiod")
        if error:
            raise ValidationError([error], cls)  # type: ignore
        return value
