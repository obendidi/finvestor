import os
import random
from typing import AsyncGenerator

import numpy as np
import pytest
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def rng_seed():
    random.seed(0)
    np.random.seed(0)


@pytest.fixture(scope="session")
def data_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "__data__")


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "ignore_localhost": True,
        "record_mode": "none",
    }


@pytest.fixture(scope="module")
def vcr_cassette_dir(request) -> str:
    tests_dir = os.path.dirname(__file__)
    return os.path.join(tests_dir, "__cassettes__")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client(anyio_backend) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient() as client:
        yield client
