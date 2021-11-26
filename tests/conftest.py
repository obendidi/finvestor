import os
import random
from pathlib import Path
from typing import AsyncGenerator, Union

import numpy as np
import pytest
from httpx import AsyncClient
from syrupy.extensions.amber import AmberSnapshotExtension


class SameFileSnapshotExt(AmberSnapshotExtension):
    def get_snapshot_name(self, *, index: Union[str, int] = 0) -> str:
        """Get the snapshot name for the assertion index in a test location"""
        assert isinstance(
            index, str
        ), "Index should filename and snapshot name to use this extension"
        return index

    def get_location(self, *, index: Union[str, int]) -> str:
        """Returns full location where snapshot data is stored."""
        assert isinstance(
            index, str
        ), "Index should filename and snapshot name to use this extension"
        return os.path.join(self._dirname, f"{index}.{self._file_extension}")


class SameNameSnapshotExt(AmberSnapshotExtension):
    def get_snapshot_name(self, *, index: Union[str, int] = 0) -> str:
        """Get the snapshot name for the assertion index in a test location"""
        assert isinstance(index, str)
        return index


@pytest.fixture
def same_file_snapshot(snapshot):
    return snapshot.use_extension(SameFileSnapshotExt)


@pytest.fixture
def same_name_snapshot(snapshot):
    return snapshot.use_extension(SameNameSnapshotExt)


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(os.path.join(os.path.dirname(__file__), "__data__"))


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client(anyio_backend) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient() as client:
        yield client


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "ignore_localhost": True,
        "record_mode": "once",
    }


@pytest.fixture(scope="module")
def vcr_cassette_dir(request) -> str:
    tests_dir = os.path.dirname(__file__)
    return os.path.join(tests_dir, "__cassettes__")


@pytest.fixture(autouse=True)
def rng_seed():
    random.seed(0)
    np.random.seed(0)
