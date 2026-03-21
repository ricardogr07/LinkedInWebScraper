from __future__ import annotations

import logging
import os
import shutil
from io import StringIO
from pathlib import Path

import linkedin_web_scraper.infra.paths as paths
from linkedin_web_scraper.infra.logging import (
    PACKAGE_LOGGER_NAME,
    configure_logging,
    get_logger,
    resolve_logger,
)
from Utils.logger import Logger

TEST_TMP_ROOT = Path(".tmp") / "phase3-logger-tests"


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
    assert logger1.file_path == os.devnull
    assert logger1.log.name == PACKAGE_LOGGER_NAME


def test_configure_logging_writes_to_stream():
    stream = StringIO()
    logger = configure_logging(stream=stream, filename=None, force=True)

    logger.info("hello")

    assert "hello" in stream.getvalue()
    assert logger.name == PACKAGE_LOGGER_NAME


def test_configure_logging_resolves_relative_files_to_managed_logs_directory(monkeypatch):
    managed_logs_dir = TEST_TMP_ROOT / "managed-logs"
    if managed_logs_dir.exists():
        shutil.rmtree(managed_logs_dir)
    monkeypatch.setattr(paths, "DEFAULT_LOGS_DIR", managed_logs_dir)

    logger = configure_logging(filename="phase3.log", force=True)
    logger.info("phase3-check")

    for handler in logger.handlers[:]:
        handler.flush()
        handler.close()
        logger.removeHandler(handler)

    assert (managed_logs_dir / "phase3.log").exists()
    assert "phase3-check" in (managed_logs_dir / "phase3.log").read_text(encoding="utf-8")

    shutil.rmtree(managed_logs_dir)


def test_resolve_logger_prefers_wrapped_log():
    wrapped_logger = logging.getLogger("wrapped-test")
    wrapper = type("Wrapper", (), {"log": wrapped_logger})()

    assert resolve_logger(wrapper, name="ignored") is wrapped_logger
