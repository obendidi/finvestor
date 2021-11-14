import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(os.path.join(os.path.dirname(__file__), "__data__"))
