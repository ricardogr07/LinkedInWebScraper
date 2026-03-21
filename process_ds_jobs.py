from __future__ import annotations

from pathlib import Path

import pandas as pd

from linkedin_web_scraper.application.daily_scrape_service import DailyScrapeService
from LinkedInWebScraper.job_scraper_config_factory import JobScraperConfigFactory
from Utils.logger import Logger


def run_ds_daily_scraper(
    logger: Logger,
    openai_enabled: bool = False,
    position: str = "Data Scientist",
    location: str = "Monterrey",
    time_posted: str = "DAY",
    file_name: str | None = None,
    output_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Compatibility wrapper for running the legacy daily scrape flow."""
    service = DailyScrapeService(logger=logger, config_factory=JobScraperConfigFactory)
    return service.run_for_location(
        position=position,
        location=location,
        openai_enabled=openai_enabled,
        time_posted=time_posted,
        file_name=file_name,
        output_dir=output_dir,
    )
