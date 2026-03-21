from __future__ import annotations

import logging
from unittest.mock import MagicMock

from Utils.logger import Logger


def setup_function() -> None:
    logging.shutdown()
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    Logger._instance = None


def test_logger_singleton_and_basic_config(monkeypatch):
    basic_config = MagicMock()
    get_logger = MagicMock()
    monkeypatch.setattr(logging, "basicConfig", basic_config)
    monkeypatch.setattr(logging, "getLogger", get_logger)

    logger1 = Logger("first.log")
    logger2 = Logger("second.log")

    assert logger1 is logger2
    basic_config.assert_called_once_with(
        filename="first.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True,
    )
    get_logger.assert_called_once()


def test_logger_exposes_underlying_logger(monkeypatch):
    basic_config = MagicMock()
    logger_instance = MagicMock()
    monkeypatch.setattr(logging, "basicConfig", basic_config)
    monkeypatch.setattr(logging, "getLogger", MagicMock(return_value=logger_instance))

    logger = Logger("test.log")
    logger.log.info("hello")

    logger_instance.info.assert_called_once_with("hello")
