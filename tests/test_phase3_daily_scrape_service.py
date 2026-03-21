from __future__ import annotations

import logging
import shutil
from pathlib import Path

import pandas as pd

from linkedin_web_scraper.application.daily_scrape_service import (
    DailyScrapeService,
    format_jobs_output_name,
    resolve_output_path,
)
from linkedin_web_scraper.config.options import RemoteType


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

    def __init__(self, logger, config):
        self.config = config

    def generate_file_name(self) -> str:
        return "generated.csv"

    def save_jobs_to_csv(self, df, file_name=None, append=True):
        FakeFileManager.saved_call = {
            "df": df.copy(),
            "file_name": file_name,
            "append": append,
            "config_remote": str(self.config.remote),
        }


def test_format_jobs_output_name_uses_stable_names():
    assert format_jobs_output_name("Data Scientist", "Mexico City") == "LinkedIn_Jobs_Data_Scientist_Mexico_City.csv"


def test_resolve_output_path_uses_output_directory():
    target_dir = Path("phase3-output-test")
    if target_dir.exists():
        shutil.rmtree(target_dir)

    resolved = resolve_output_path("jobs.csv", target_dir)

    assert resolved == str(target_dir / "jobs.csv")
    assert target_dir.exists()

    shutil.rmtree(target_dir)


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

    output_dir = Path("phase3-service-output")
    if output_dir.exists():
        shutil.rmtree(output_dir)

    combined = service.run_for_location(location="Monterrey", output_dir=output_dir)

    assert list(combined["Remote"]) == [
        str(RemoteType.REMOTE),
        str(RemoteType.HYBRID),
        str(RemoteType.ON_SITE),
    ]
    assert FakeFileManager.saved_call["file_name"] == str(output_dir / "generated.csv")
    assert FakeFileManager.saved_call["config_remote"] == str(RemoteType.ALL)

    shutil.rmtree(output_dir)
