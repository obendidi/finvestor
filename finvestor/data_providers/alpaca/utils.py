from finvestor.data_providers.schemas import AutoValidInterval
from finvestor.data_providers.utils import parse_duration


def convert_interval_to_alpaca_timeframe(interval: AutoValidInterval) -> str:
    if interval == "auto":
        return "1Min"
    delta = parse_duration(interval)
    if delta.days > 0:
        return f"{delta.days}Day"
    elif delta.seconds >= 3600:
        return f"{int(delta.seconds/3600)}Hour"
    else:
        return f"{int(delta.seconds/60)}Min"
