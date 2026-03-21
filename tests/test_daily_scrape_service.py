from __future__ import annotations

import logging
import shutil
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from linkedin_web_scraper.application.daily_scrape_service import (
    DailyScrapeService,
    format_jobs_output_name,
    resolve_output_path,
)
from linkedin_web_scraper.config.options import RemoteType
from linkedin_web_scraper.infra import paths

TEST_TMP_ROOT = Path(".tmp") / "daily-service-tests"


class FakeScraper:
    def __init__(self, logger, config):
        self.config = config

    def run(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "Title": "Data Scientist",
                    "Location": self.config.location,
                    "Remote": str(self.config.remote),
                }
            ]
        )


class FakeFileManager:
    saved_call = None

    def __init__(self, logger, config, *, output_dir=None):
        self.config = config
        self.output_dir = output_dir

    def generate_file_name(self) -> str:
        return "generated.csv"

    def save_jobs_to_csv(self, df, file_name=None, append=True):
        FakeFileManager.saved_call = {
            "df": df.copy(),
            "file_name": file_name,
            "append": append,
            "config_remote": str(self.config.remote),
            "output_dir": self.output_dir,
        }


def _reset_test_directory(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_format_jobs_output_name_uses_stable_names():
    assert (
        format_jobs_output_name("Data Scientist", "Mexico City")
        == "LinkedIn_Jobs_Data_Scientist_Mexico_City.csv"
    )


def test_resolve_output_path_uses_output_directory():
    target_dir = TEST_TMP_ROOT / "explicit-output-dir"
    _reset_test_directory(target_dir)

    resolved = resolve_output_path("jobs.csv", target_dir)

    assert resolved == str(target_dir / "jobs.csv")
    assert target_dir.exists()

    shutil.rmtree(target_dir)


def test_resolve_output_path_defaults_to_managed_jobs_directory(monkeypatch):
    managed_dir = _reset_test_directory(TEST_TMP_ROOT / "managed-jobs")
    monkeypatch.setattr(paths, "DEFAULT_JOBS_OUTPUT_DIR", managed_dir)

    resolved = resolve_output_path("jobs.csv")

    assert resolved == str(managed_dir / "jobs.csv")
    assert managed_dir.exists()

    shutil.rmtree(managed_dir)


def test_daily_scrape_service_combines_remote_runs_and_saves_to_output_dir():
    logger = logging.getLogger("phase3-daily-service")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    FakeFileManager.saved_call = None

    service = DailyScrapeService(
        logger=logger,
        scraper_cls=FakeScraper,
        file_manager_cls=FakeFileManager,
    )

    output_dir = _reset_test_directory(TEST_TMP_ROOT / "service-output")

    combined = service.run_for_location(location="Monterrey", output_dir=output_dir)

    assert list(combined["Remote"]) == [
        str(RemoteType.REMOTE),
        str(RemoteType.HYBRID),
        str(RemoteType.ON_SITE),
    ]
    assert FakeFileManager.saved_call["file_name"] is None
    assert FakeFileManager.saved_call["output_dir"] == output_dir
    assert FakeFileManager.saved_call["config_remote"] == str(RemoteType.ALL)

    shutil.rmtree(output_dir)


def test_daily_scrape_service_defaults_named_outputs_to_managed_directory(monkeypatch):
    logger = logging.getLogger("phase3-daily-service-default-output")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    FakeFileManager.saved_call = None
    managed_dir = _reset_test_directory(TEST_TMP_ROOT / "named-managed-jobs")
    monkeypatch.setattr(paths, "DEFAULT_JOBS_OUTPUT_DIR", managed_dir)

    service = DailyScrapeService(
        logger=logger,
        scraper_cls=FakeScraper,
        file_manager_cls=FakeFileManager,
    )

    service.run_for_location(location="Monterrey", file_name="custom.csv")

    assert FakeFileManager.saved_call["file_name"] == str(managed_dir / "custom.csv")

    shutil.rmtree(managed_dir)


def test_run_daily_defaults_combined_output_to_managed_directory(monkeypatch):
    logger = logging.getLogger("phase3-daily-service-run-daily")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    managed_dir = _reset_test_directory(TEST_TMP_ROOT / "combined-managed-jobs")
    monkeypatch.setattr(paths, "DEFAULT_JOBS_OUTPUT_DIR", managed_dir)

    service = DailyScrapeService(
        logger=logger,
        scraper_cls=FakeScraper,
        file_manager_cls=FakeFileManager,
    )

    with patch("pandas.DataFrame.to_csv") as to_csv_mock:
        combined = service.run_daily(cities=("Monterrey",))

    assert combined.shape[0] == 3
    to_csv_mock.assert_called_once_with(
        str(managed_dir / "LinkedIn_Jobs_Data_Scientist_Mexico.csv"),
        index=False,
    )

    shutil.rmtree(managed_dir)

