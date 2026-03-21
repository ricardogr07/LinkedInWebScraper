from __future__ import annotations

import logging
import os
from io import StringIO

from linkedin_web_scraper.infra.logging import (
    PACKAGE_LOGGER_NAME,
    configure_logging,
    get_logger,
    resolve_logger,
)
from Utils.logger import Logger


def setup_function() -> None:
    logger = get_logger(PACKAGE_LOGGER_NAME)
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    logger.addHandler(logging.NullHandler())
    Logger._instance = None


def test_logger_singleton_and_named_logger():
    logger1 = Logger(os.devnull)
    logger2 = Logger("second.log")

    assert logger1 is logger2
    assert logger1.filename == os.devnull
    assert logger1.log.name == PACKAGE_LOGGER_NAME


def test_configure_logging_writes_to_stream():
    stream = StringIO()
    logger = configure_logging(stream=stream, filename=None, force=True)

    logger.info("hello")

    assert "hello" in stream.getvalue()
    assert logger.name == PACKAGE_LOGGER_NAME


def test_resolve_logger_prefers_wrapped_log():
    wrapped_logger = logging.getLogger("wrapped-test")
    wrapper = type("Wrapper", (), {"log": wrapped_logger})()

    assert resolve_logger(wrapper, name="ignored") is wrapped_logger
