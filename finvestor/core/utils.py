import importlib.resources
import logging.config

import yaml

import finvestor.core

YAHOO_FINANCE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    )
}


def setup_logging() -> None:
    config = yaml.safe_load(
        importlib.resources.read_text(finvestor.core, "logging.yml")
    )
    logging.config.dictConfig(config)
