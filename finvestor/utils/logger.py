import importlib.resources
import logging
import logging.config
import os
import typing as tp
from datetime import datetime
from pathlib import Path

import yaml
from rich.console import ConsoleRenderable
from rich.logging import RichHandler as _RichHandler
from rich.traceback import Traceback

import finvestor


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
        message_renderable: ConsoleRenderable,
    ) -> ConsoleRenderable:

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


def setup_logging(
    logging_file: tp.Union[None, Path, str] = None,
    default_level: tp.Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG",
    default_format: str = "%(message)s",
    default_datefmt: str = "[%x %X]",
) -> None:

    # check env
    logging_file = logging_file or os.getenv("FINVESTOR_LOGGING_FILE")

    try:
        if logging_file is not None:
            if isinstance(logging_file, str):
                logging_file = Path(logging_file)
            config = yaml.safe_load(logging_file.read_bytes())
        else:
            config = yaml.safe_load(
                importlib.resources.read_text(finvestor, "logging.yaml")
            )
        logging.config.dictConfig(config)
    except Exception as error:
        print(f"Failed to load logging config file: <{error}>")
        print("Using default logging config.")
        logging.basicConfig(
            level=default_level,
            format=default_format,
            datefmt=default_datefmt,
            handlers=[RichHandler()],
        )


if __name__ == "__main__":
    setup_logging()

    logger = logging.getLogger(__name__)

    logger.debug("This a debug message ....")
    logger.info("This an info message ....")
    logger.warning("This a warning message ....")
    logger.error("This an error message ....")
    logger.critical("This a critical message ....")
