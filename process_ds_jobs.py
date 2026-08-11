from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from linkedin_web_scraper import JobScraperConfigFactory, Logger
from linkedin_web_scraper.application.daily_scrape_service import DailyScrapeService
from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL
from linkedin_web_scraper.config.options import EnrichmentProvider
from linkedin_web_scraper.interfaces.cli.main import main as cli_main


def run_ds_daily_scraper(
    logger: Logger,
    enrichment_provider: EnrichmentProvider = EnrichmentProvider.NONE,
    enrichment_model: str = DEFAULT_OPENAI_MODEL,
    position: str = "Data Scientist",
    location: str = "Monterrey",
    time_posted: str = "DAY",
    file_name: str | None = None,
    output_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Run the daily scrape flow through the canonical application service."""
    service = DailyScrapeService(logger=logger, config_factory=JobScraperConfigFactory)
    return service.run_for_location(
        position=position,
        location=location,
        enrichment_provider=enrichment_provider,
        enrichment_model=enrichment_model,
        time_posted=time_posted,
        file_name=file_name,
        output_dir=output_dir,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the legacy once-scrape compatibility entrypoint via the package CLI."""
    return cli_main(list(argv) if argv is not None else ["scrape", "once"])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or ["scrape", "once"]))
