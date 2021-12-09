import logging
import logging.config
import typing as tp
from datetime import datetime

from pydantic.utils import deep_update
from rich.console import ConsoleRenderable
from rich.logging import RichHandler as _RichHandler
from rich.traceback import Traceback


class RichHandler(_RichHandler):
    def __init__(self):
        super().__init__(
            show_time=True,
            show_level=True,
            rich_tracebacks=True,
            show_path=True,
            enable_link_path=False,
        )

    def render(
        self,
        *,
        record: logging.LogRecord,
        traceback: tp.Optional[Traceback],
        message_renderable: "ConsoleRenderable",
    ) -> "ConsoleRenderable":

        path = record.name
        level = self.get_level_text(record)
        time_format = None if self.formatter is None else self.formatter.datefmt
        log_time = datetime.fromtimestamp(record.created)

        log_renderable = self._log_render(
            self.console,
            [message_renderable] if not traceback else [message_renderable, traceback],
            log_time=log_time,
            time_format=time_format,
            level=level,
            path=path,
            link_path=record.pathname if self.enable_link_path else None,
        )
        return log_renderable


DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        }
    },
    "handlers": {
        "default": {"class": RichHandler},
    },
    "root": {"level": "DEBUG", "handlers": ["default"], "propogate": False},
    # "loggers": {
    #     "finvestor": {"level": "DEBUG"},
    #     "httpx": {"level": "INFO"},
    #     "matplotlib": {"level": "INFO"},
    #     "PIL": {"level": "INFO"},
    # },
}


def setup_logging(
    update_config: tp.Optional[tp.Dict[str, tp.Any]] = None,
) -> None:
    if update_config is not None:
        config = deep_update(DEFAULT_CONFIG, update_config)
    else:
        config = DEFAULT_CONFIG

    logging.config.dictConfig(config)
