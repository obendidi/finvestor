import typing as tp
from collections.abc import Sequence

import pandas as pd
from pydantic import BaseModel, Extra, Field, PrivateAttr

__all__ = ("BaseDataFrameModel", "BaseAsset")

T = tp.TypeVar("T", bound="BaseDataFrameModel")
SequenceOfObjects = tp.Sequence[tp.Union[BaseModel, tp.Mapping]]


class BaseDataFrameModel(BaseModel, Sequence):
    __root__: SequenceOfObjects
    _df: tp.Optional[pd.DataFrame] = PrivateAttr(default=None)

    @classmethod
    def build(cls: tp.Type[T], data: SequenceOfObjects) -> T:
        return cls(__root__=data)

    def __getitem__(self, i) -> tp.Any:
        return self.__root__[i]

    def __len__(self) -> int:
        return len(self.__root__)

    def dict(self) -> tp.List[tp.Dict]:  # type: ignore
        data: tp.Dict[str, tp.List[tp.Any]] = super().dict()
        return data.get("__root__", [])

    @property
    def df(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df
        df = pd.json_normalize(self.dict(), sep="_", max_level=2)
        self._df = df.dropna(how="all")
        return self._df

    class Config:
        extra = Extra.forbid
        allow_mutation = False


class BaseAsset(BaseModel):
    ticker: str = Field(..., repr=True)
    name: tp.Optional[str] = Field(repr=False)
    type: tp.Optional[str] = Field(repr=False)
    currency: tp.Optional[str] = Field(repr=False)
    exchange: tp.Optional[str] = Field(repr=False)
    exchange_timezone: tp.Optional[str] = Field(repr=False)
    market: tp.Optional[str] = Field(repr=False)
    isin: tp.Optional[str] = Field(repr=False)
    country: tp.Optional[str] = Field(repr=False)
    sector: tp.Optional[str] = Field(repr=False)
    industry: tp.Optional[str] = Field(repr=False)

    def __repr_args__(self):
        # TODO: remove when latest version of pydantic is deployed
        return [
            (k, v)
            for k, v in self.__dict__.items()
            if self.__fields__[k].field_info.extra.get("repr", True)
        ]
