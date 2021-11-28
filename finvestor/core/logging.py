import importlib.resources
import logging.config

import yaml
from rich.logging import RichHandler as _RichHandler

import finvestor.core


class RichHandler(_RichHandler):
    def __init__(self):
        super().__init__(
            show_time=True,
            omit_repeated_times=False,
            show_level=True,
            rich_tracebacks=True,
        )


def setup_logging() -> None:
    config = yaml.safe_load(
        importlib.resources.read_text(finvestor.core, "logging.yml")
    )
    logging.config.dictConfig(config)
