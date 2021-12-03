import typing as tp
from collections.abc import Sequence

import pandas as pd
from pydantic import BaseModel

__all__ = "BaseDataFrameModel"

T = tp.TypeVar("T", bound="BaseDataFrameModel")
SequenceOfObjects = tp.Sequence[tp.Union[BaseModel, tp.Mapping]]


class BaseDataFrameModel(BaseModel, Sequence):
    __root__: SequenceOfObjects

    @classmethod
    def build(cls: tp.Type[T], data: SequenceOfObjects) -> T:
        return cls(__root__=data)

    @classmethod
    def from_dataframe(cls: tp.Type[T], data: pd.DataFrame) -> T:
        records: tp.List[tp.Mapping] = data.to_dict(orient="records")  # type: ignore
        return cls.build(records)

    def __getitem__(self, i) -> SequenceOfObjects:
        return self.__root__[i]

    def __len__(self) -> int:
        return len(self.__root__)

    def df(self) -> pd.DataFrame:
        data = self.dict()
        df = pd.DataFrame(data.get("__root__"))
        df = df.dropna(how="all")
        return df

    def append(self, data: tp.Any) -> None:
        pass
