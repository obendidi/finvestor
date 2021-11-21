import importlib.resources
import logging.config

import yaml

import finvestor.core


def setup_logging() -> None:
    config = yaml.safe_load(
        importlib.resources.read_text(finvestor.core, "logging.yml")
    )
    logging.config.dictConfig(config)
