import typing as tp
from datetime import datetime

import pytz
from pydantic import Field

from finvestor.core.timeframe import parse_duration
from finvestor.data_providers.alpaca.settings import alpaca_settings
from finvestor.data_providers.alpaca.utils import convert_interval_to_alpaca_timeframe
from finvestor.data_providers.schemas import BaseBarsRequestParams


class APCABarsRequestParams(BaseBarsRequestParams):

    limit: tp.Optional[int] = Field(None, ge=1, le=10000)
    adjustment: tp.Literal[None, "raw", "split", "dividend", "all"] = None

    def params(
        self, end_default: tp.Literal["now", "interval"] = "now", **kwargs: tp.Any
    ) -> tp.Dict[str, tp.Any]:
        data = super().params(**kwargs)

        # set timeframe
        data["timeframe"] = convert_interval_to_alpaca_timeframe(data.pop("interval"))

        # if we have start but not end
        if "start" in data:
            if "end" not in data:
                data["end"] = (
                    datetime.now(tz=pytz.UTC) - alpaca_settings.HISTORICAL_DATA_DELAY
                    if end_default == "now"
                    # we set it to start + interval*2 to make sure we get enough data
                    else data["start"] + parse_duration(data["timeframe"]) * 2
                )

        # convert period to start-end
        # TODO: doesn't take into account days where the market is not Open
        # (holidays, weekends, ..)
        # maybe have a look at: https://github.com/rsheftel/pandas_market_calendars
        if "period" in data:
            period = data.pop("period")
            data["end"] = (
                datetime.now(tz=pytz.UTC) - alpaca_settings.HISTORICAL_DATA_DELAY
            )
            data["start"] = data["end"] - parse_duration(period)

        data["start"] = data["start"].isoformat()
        data["end"] = data["end"].isoformat()
        return data
