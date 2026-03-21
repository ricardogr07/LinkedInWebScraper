from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Protocol, TextIO, runtime_checkable

PACKAGE_LOGGER_NAME = "linkedin_web_scraper"
DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


@runtime_checkable
class SupportsLogAttribute(Protocol):
    """Protocol for legacy logger wrappers that expose a `.log` logger."""

    log: logging.Logger


package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
if not any(isinstance(handler, logging.NullHandler) for handler in package_logger.handlers):
    package_logger.addHandler(logging.NullHandler())


def parse_log_level(level: int | str) -> int:
    """Normalize string and integer log levels to logging constants."""
    if isinstance(level, int):
        return level

    normalized = getattr(logging, level.upper(), None)
    if not isinstance(normalized, int):
        raise ValueError(f"Unsupported log level: {level}")
    return normalized


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a package logger or a named descendant logger."""
    return logging.getLogger(name or PACKAGE_LOGGER_NAME)


def resolve_logger(
    logger: logging.Logger | SupportsLogAttribute | None = None,
    *,
    name: str | None = None,
) -> logging.Logger:
    """Resolve stdlib loggers and legacy wrappers to a standard logger instance."""
    if logger is None:
        return get_logger(name)
    if isinstance(logger, logging.Logger):
        return logger

    wrapped_logger = getattr(logger, "log", None)
    if wrapped_logger is not None:
        return wrapped_logger

    return logger


def configure_logging(
    filename: str | Path | None = None,
    *,
    level: int | str = logging.INFO,
    stream: TextIO | None = None,
    logger_name: str = PACKAGE_LOGGER_NAME,
    force: bool = True,
    format_string: str = DEFAULT_LOG_FORMAT,
) -> logging.Logger:
    """Configure package logging for scripts and CLI entrypoints."""
    configured_level = parse_log_level(level)
    logger = get_logger(logger_name)
    logger.setLevel(configured_level)
    logger.propagate = False

    if force:
        logger.handlers.clear()

    formatter = logging.Formatter(format_string)
    handlers: list[logging.Handler] = []

    if filename is not None:
        handlers.append(logging.FileHandler(filename, encoding="utf-8"))

    handlers.append(logging.StreamHandler(stream or sys.stderr))

    for handler in handlers:
        handler.setLevel(configured_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class Logger:
    """Backward-compatible logger facade that configures package logging once."""

    _instance: Logger | None = None

    def __new__(cls, filename: str | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, filename: str | None = None):
        if getattr(self, "_initialized", False):
            return

        self.filename = filename
        self.log = configure_logging(filename=filename)
        self._initialized = True


__all__ = [
    "DEFAULT_LOG_FORMAT",
    "Logger",
    "PACKAGE_LOGGER_NAME",
    "configure_logging",
    "get_logger",
    "parse_log_level",
    "resolve_logger",
]
