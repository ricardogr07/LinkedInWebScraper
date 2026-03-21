from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from LinkedInWebScraper.job_scraper import JobScraper
from LinkedInWebScraper.job_scraper_config import JobScraperConfig

ROOT = Path(__file__).resolve().parents[1]


def test_extract_job_info_from_fixture():
    html = (ROOT / "tests" / "fixtures" / "linkedin_job_listing.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    job = soup.find("li")

    logger = MagicMock()
    logger.log = MagicMock()
    scraper = JobScraper(
        config=JobScraperConfig(position="Data Scientist", location="Monterrey"),
        logger=logger,
    )

    job_info = scraper.extract_job_info(job)

    assert job_info == {
        "Location": "Monterrey, Nuevo Leon, Mexico",
        "Title": "Data Scientist",
        "Company": "Acme Corp",
        "Url": "https://www.linkedin.com/jobs/view/1234567890/?position=1",
        "Remote": "ALL",
    }
