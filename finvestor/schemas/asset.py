from pydantic import BaseModel

__all__ = "BaseAsset"


class BaseAsset(BaseModel):
    ticker: str
    name: str
    type: str
