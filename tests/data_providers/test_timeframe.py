from datetime import timedelta
from typing import Literal
from finvestor.data_providers.timeframe import TimeFrame
from pydantic import BaseModel, ValidationError
import pytest


def test_timeframe_without_subtype():
    class Model(BaseModel):
        timeframe: TimeFrame

    model = Model(timeframe=TimeFrame("1m"))
    assert model.timeframe.timeperiod == "1m"


def test_str_timeframe_without_subtype():
    class Model(BaseModel):
        timeframe: TimeFrame

    with pytest.raises(ValidationError):
        Model(timeframe="1m")


@pytest.mark.parametrize(
    "timeframe_type_with_subtype, value",
    [
        (TimeFrame[str], ["1m"]),
        (TimeFrame[int], "1m"),
        (TimeFrame[Literal["1m", "2m"]], "1mo"),
        (TimeFrame[Literal["1m", "2m"]], TimeFrame("1mo")),
    ],
)
def test_timeframe_with_subtypes_validation_error(timeframe_type_with_subtype, value):
    class Model(BaseModel):
        timeframe: timeframe_type_with_subtype

    with pytest.raises(ValidationError):
        Model(timeframe=value)


@pytest.mark.parametrize(
    "timeframe_type_with_subtype, value",
    [
        (TimeFrame[str], "1m"),
        (TimeFrame[int], 42),
        (TimeFrame[Literal["1m", "2m"]], "1m"),
    ],
)
def test_timeframe_with_subtypes(timeframe_type_with_subtype, value):
    class Model(BaseModel):
        timeframe: timeframe_type_with_subtype

    model = Model(timeframe=value)
    assert model.timeframe == TimeFrame(value)


def test_timeframe_with_subtypes_and_timeframe_value():
    class Model(BaseModel):
        timeframe: TimeFrame[Literal["1m", "2m"]]

    model = Model(timeframe=TimeFrame("1m"))
    assert model.timeframe.timeperiod == "1m"


def test_timeframe_equal_ops():
    t1 = TimeFrame("1m")
    t2 = TimeFrame("1minute")
    t3 = TimeFrame("60s")
    t4 = TimeFrame(timedelta(minutes=1))
    assert t1 == t2 == t3 == t4


def test_timeframe_order_ops():
    t1 = TimeFrame("1m")
    t2 = TimeFrame("1minute 3s")
    t3 = TimeFrame("1h")
    t4 = TimeFrame(timedelta(days=1))
    assert t1 < t2 < t3 < t4
    assert not (t4 < t1)
