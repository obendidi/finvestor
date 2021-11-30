import typing as tp
from datetime import datetime

import pytz
from pydantic import BaseModel

from finvestor.core.timeframe import parse_duration
from finvestor.data_providers.schemas import BaseBarsRequestParams
from finvestor.data_providers.yahoo_finance.utils import get_smallest_valid_interval


class YFBarsRequestParams(BaseBarsRequestParams):
    include_prepost: tp.Optional[bool] = None
    events: tp.Literal[None, "div", "split", "div,splits"] = None

    def params(
        self, end_default: tp.Literal["now", "interval"] = "now", **kwargs: tp.Any
    ) -> tp.Dict[str, tp.Any]:
        data = super().params(**kwargs)
        if data["interval"] == "auto":
            data["interval"] = get_smallest_valid_interval(**data)
        if "include_prepost" in data:
            data["includePrePost"] = data.pop("include_prepost")
        if "period" in data:
            data["range"] = data.pop("period")

        if "start" in data:
            if "end" not in data:
                data["end"] = (
                    datetime.now(tz=pytz.UTC)
                    if end_default == "now"
                    # we set it to start + interval*2 to make sure we get enough data
                    else data["start"] + parse_duration(data["interval"]) * 2
                )
            data["period1"] = int(datetime.timestamp(data.pop("start")))
            data["period2"] = int(datetime.timestamp(data.pop("end")))
        return data


class YfOpenHighLowClose(BaseModel):
    timestamp: tp.List[datetime]
    volume: tp.List[tp.Optional[float]]
    open: tp.List[tp.Optional[float]]
    high: tp.List[tp.Optional[float]]
    low: tp.List[tp.Optional[float]]
    close: tp.List[tp.Optional[float]]
