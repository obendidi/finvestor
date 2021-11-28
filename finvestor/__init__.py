import importlib.metadata as importlib_metadata

from finvestor.core import FinvestorConfig, setup_logging

setup_logging()
config = FinvestorConfig()

__version__ = importlib_metadata.version(__name__)
