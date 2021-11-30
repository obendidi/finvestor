import typing as tp

from httpx import HTTPError


class BaseHTTPError(HTTPError):
    def __init__(
        self,
        *,
        ticker: str,
        params: tp.Dict[str, tp.Any],
        status_code: int,
        error: tp.Any,
        data_provider: str,
    ) -> None:
        message = (
            f"[{data_provider.upper()}] (ticker={ticker}) "
            f"(params={params}) responded with (code={status_code}):  "
            f"{error}"
        )
        super().__init__(message)


class UnprocessableEntity(BaseHTTPError):
    pass


class EmptyBars(BaseHTTPError):
    pass
