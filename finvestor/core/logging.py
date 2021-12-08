import importlib.resources
import logging
import logging.config
import typing as tp
from datetime import datetime

import yaml
from rich.console import ConsoleRenderable
from rich.logging import RichHandler as _RichHandler
from rich.traceback import Traceback

import finvestor.core


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


def setup_logging() -> None:
    config = yaml.safe_load(
        importlib.resources.read_text(finvestor.core, "logging.yml")
    )
    logging.config.dictConfig(config)
