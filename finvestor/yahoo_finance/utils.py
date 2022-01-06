import random
import typing as tp
from datetime import datetime, timezone

from pydantic import BaseModel, Field, validator
from pydantic.fields import ModelField

from finvestor.utils.duration import parse_duration

YF_CHART_URI = "https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
YF_QUOTE_URI = "https://finance.yahoo.com/quote/{ticker}"
ISIN_URI = "https://markets.businessinsider.com/ajax/SearchController_Suggest"

ValidInterval = tp.Literal[
    "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"
]
ValidPeriod = tp.Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd"
]
AutoValidInterval = tp.Union[tp.Literal["auto"], ValidInterval]


VALID_INTERVALS: tp.Tuple[ValidInterval, ...] = tp.get_args(ValidInterval)
MAX_DAYS_TO_VALID_INTERVALS: tp.Dict[float, tp.Tuple[ValidInterval, ...]] = {
    7: VALID_INTERVALS,  # all
    59.9: VALID_INTERVALS[1:],  # 2m and above
    729.9: VALID_INTERVALS[5:],  # 1h and above
}
# by default smallest always valid interval is 1d
DEFAULT_VALID_INTERVALS: tp.Tuple[ValidInterval, ...] = VALID_INTERVALS[6:]


# List of user agent taken from:
# https://github.com/dpguthrie/yahooquery/blob/a30cc310bf5eb4b5ce5eadeafe51d589995ea9fd/yahooquery/utils/__init__.py#L15
USER_AGENT_LIST: tp.List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",  # noqa
]


def user_agent_header() -> tp.Dict[str, str]:
    return {"User-Agent": random.choice(USER_AGENT_LIST)}


class YFBarsRequestParams(BaseModel):
    include_prepost: tp.Optional[bool] = Field(alias="includePrePost")
    events: tp.Literal[None, "div", "split", "div,splits"] = "div,splits"
    start: tp.Union[None, int] = Field(alias="period1")
    period: tp.Optional[ValidPeriod] = Field(alias="range")
    interval: AutoValidInterval
    end: tp.Union[None, int] = Field(alias="period2")

    @validator("period", always=True)
    def check_start_or_period(
        cls, period: tp.Optional[ValidPeriod], values
    ) -> tp.Optional[ValidPeriod]:
        start = values.get("start")
        if start is None and period is None:
            raise ValueError("Missing values: 'period' or 'start'.")
        if start is not None and period is not None:
            raise ValueError("Duplicate values: 'period' and 'start'.")
        return period

    @validator("start", "end", pre=True)
    def check_start_end(
        cls, value: tp.Any, field: ModelField, values
    ) -> tp.Optional[int]:
        if value is None:
            return value
        if values.get("period") is not None:
            raise ValueError(f"Duplicate values: 'period' and '{field.name}'.")
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, datetime):
            if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
                raise ValueError(f"Missing {field.name} timezone info: {value}")
            if value.tzinfo != timezone.utc:
                value = value.astimezone(timezone.utc)

            return int(datetime.timestamp(value))
        else:
            raise TypeError(
                f"Only 'int' or 'datetime' values are supported for field {field.name}"
                f", got: {type(value)}"
            )

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True


def get_valid_intervals(params: YFBarsRequestParams) -> tp.Tuple[ValidInterval, ...]:
    if params.period is not None:
        delta = parse_duration(params.period)
    elif params.start is not None:
        delta = datetime.now(tz=timezone.utc) - datetime.fromtimestamp(params.start)

    for max_days, valid_intervals in MAX_DAYS_TO_VALID_INTERVALS.items():
        if delta.days <= max_days:
            return valid_intervals
    return DEFAULT_VALID_INTERVALS


def extract_tickers_list(tickers: tp.Union[str, tp.List[str]]) -> tp.List[str]:
    if isinstance(tickers, str):
        return tickers.split(",")
    else:
        _tickers = []
        for ticker in tickers:
            _tickers.extend(extract_tickers_list(ticker))
        return _tickers
