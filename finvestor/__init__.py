import importlib.metadata as importlib_metadata

from finvestor.core import setup_logging

setup_logging()

__version__ = importlib_metadata.version(__name__)
