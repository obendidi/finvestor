from httpx import Request

from finvestor import config


def auth(request: Request) -> Request:
    request.headers["APCA-API-KEY-ID"] = str(config.APCA_API_KEY_ID)
    request.headers["APCA-API-SECRET-KEY"] = str(config.APCA_API_SECRET_KEY)
    return request
