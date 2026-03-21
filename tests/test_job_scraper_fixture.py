from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
from bs4 import BeautifulSoup

from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
from linkedin_web_scraper.config.options import RemoteType, TimePosted
from linkedin_web_scraper.infra.http.job_scraper import JobScraper

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def _read_fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _build_scraper() -> JobScraper:
    logger = logging.getLogger("test-job-scraper")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    return JobScraper(
        config=JobScraperConfig(
            position="Data Scientist",
            location="Monterrey",
            remote=RemoteType.REMOTE,
            time_posted=TimePosted.DAY,
        ),
        logger=logger,
    )


def test_extract_job_info_from_fixture():
    html = _read_fixture_text("linkedin_job_listing.html")
    soup = BeautifulSoup(html, "html.parser")
    job = soup.find("li")
    scraper = _build_scraper()

    job_info = scraper.extract_job_info(job)

    assert job_info == {
        "Location": "Monterrey, Nuevo Leon, Mexico",
        "Title": "Data Scientist",
        "Company": "Acme Corp",
        "Url": "https://www.linkedin.com/jobs/view/1234567890/?position=1",
        "Remote": RemoteType.REMOTE,
    }


def test_generate_main_url_applies_filters():
    scraper = _build_scraper()

    url = scraper.generate_main_url()

    assert "keywords=Data%20Scientist" in url
    assert "location=Monterrey" in url
    assert "distance=10" in url
    assert "f_TPR=r86400" in url
    assert "f_WT=2" in url


def test_scrape_jobs_uses_fixture_results_when_http_is_mocked():
    scraper = _build_scraper()
    search_results = _read_fixture_text("linkedin_search_results.html")
    mocked_responses = [
        SimpleNamespace(text=search_results, content=search_results.encode("utf-8")),
        SimpleNamespace(text=search_results, content=search_results.encode("utf-8")),
    ]

    with patch(
        "linkedin_web_scraper.infra.http.job_scraper.fetch_until_success",
        side_effect=mocked_responses,
    ) as fetch_mock:
        jobs = scraper.scrape_jobs()

    assert fetch_mock.call_count == 2
    assert jobs.shape == (1, 5)
    assert jobs.iloc[0]["Title"] == "Data Scientist"
    assert jobs.iloc[0]["Company"] == "Acme Corp"
    assert jobs.iloc[0]["Remote"] == RemoteType.REMOTE


def test_fetch_job_details_parses_detail_fixture():
    scraper = _build_scraper()
    detail_html = _read_fixture_text("linkedin_job_details.html")
    df_jobs = pd.DataFrame(
        [
            {
                "Title": "Data Scientist",
                "Company": "Acme Corp",
                "Location": "Monterrey Metropolitan Area",
                "Remote": RemoteType.REMOTE,
                "Url": "https://www.linkedin.com/jobs/view/1234567890",
                "JobID": "1234567890",
            }
        ]
    )

    with patch(
        "linkedin_web_scraper.infra.http.job_scraper.fetch_until_success",
        return_value=SimpleNamespace(content=detail_html.encode("utf-8")),
    ) as fetch_mock:
        detailed_jobs = scraper.fetch_job_details(df_jobs)

    fetch_mock.assert_called_once()
    assert detailed_jobs.iloc[0]["SeniorityLevel"] == "Entry level"
    assert detailed_jobs.iloc[0]["EmploymentType"] == "Full-time"
    assert detailed_jobs.iloc[0]["JobFunction"] == "Research and Design"
    assert detailed_jobs.iloc[0]["Industries"] == "Technology"
    assert detailed_jobs.iloc[0]["PostedTime"] == "2 weeks ago"
    assert detailed_jobs.iloc[0]["NumApplicants"] == "Be among the first 25 applicants"
    assert "Python and SQL" in detailed_jobs.iloc[0]["Description"]
