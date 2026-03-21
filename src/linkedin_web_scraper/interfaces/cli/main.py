from __future__ import annotations

from linkedin_web_scraper.application.daily_scrape_service import DailyScrapeService
from linkedin_web_scraper.infra.logging import configure_logging, get_logger


def main() -> int:
    """Run the current daily scraper workflow as a temporary console entrypoint."""
    configure_logging(filename="main.log")
    logger = get_logger(__name__)
    DailyScrapeService(logger=logger).run_daily()
    return 0
