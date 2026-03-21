from __future__ import annotations

import logging

import pandas as pd

from linkedin_web_scraper.application.linkedin_job_scraper import LinkedInJobScraper
from linkedin_web_scraper.config.job_scraper_advanced_config import JobScraperAdvancedConfig
from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
from linkedin_web_scraper.domain.job_title_classifier import JobTitleClassifier


class FakeJobScraper:
    def __init__(self, scraped_jobs: pd.DataFrame, detailed_jobs: pd.DataFrame):
        self._scraped_jobs = scraped_jobs
        self._detailed_jobs = detailed_jobs
        self.received_detail_jobs: pd.DataFrame | None = None

    def scrape_jobs(self) -> pd.DataFrame:
        return self._scraped_jobs.copy()

    def fetch_job_details(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        self.received_detail_jobs = df_jobs.copy()
        return self._detailed_jobs[
            self._detailed_jobs["JobID"].isin(df_jobs["JobID"])
        ].reset_index(drop=True)


class FakeCleaner:
    def __init__(self):
        self.location_mapping = None
        self.cleaned_detail_jobs: pd.DataFrame | None = None

    def clean_jobs_dataframe(self, df_jobs: pd.DataFrame, location_mapping) -> pd.DataFrame:
        self.location_mapping = location_mapping
        return df_jobs.copy()

    def clean_extracted_job_data(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        self.cleaned_detail_jobs = df_jobs.copy()
        return df_jobs.assign(DetailsCleaned=True)

    def process_enriched_job_data(
        self, df_jobs: pd.DataFrame, skills_categories=None
    ) -> pd.DataFrame:
        return df_jobs.assign(FinalProcessed=True)


class ExplodingJobScraper:
    def scrape_jobs(self) -> pd.DataFrame:
        raise RuntimeError("boom")


LOGGER = logging.getLogger("test-linkedin-job-scraper")
LOGGER.handlers.clear()
LOGGER.addHandler(logging.NullHandler())


def test_job_title_classifier_filters_matching_rows_only():
    classifier = JobTitleClassifier(
        logger=LOGGER,
        position="Data Scientist",
        keywords=["data scientist"],
    )
    df_jobs = pd.DataFrame(
        [
            {"Title": "Senior Data Scientist"},
            {"Title": "Finance Analyst"},
        ]
    )

    classified = classifier.classify_title(df_jobs)

    assert classified["Title"].tolist() == ["Senior Data Scientist"]


def test_job_title_classifier_returns_original_when_title_column_is_missing():
    classifier = JobTitleClassifier(logger=LOGGER, position="Data Scientist", keywords=["data"])
    df_jobs = pd.DataFrame([{"Company": "Acme"}])

    classified = classifier.classify_title(df_jobs)

    assert classified.equals(df_jobs)


def test_linkedin_job_scraper_runs_pipeline_without_openai():
    scraped_jobs = pd.DataFrame(
        [
            {
                "Title": "Data Scientist",
                "Company": "Acme",
                "Location": "Monterrey",
                "Url": "https://www.linkedin.com/jobs/view/1234567890",
                "Remote": "REMOTE",
                "JobID": "1234567890",
            },
            {
                "Title": "Finance Analyst",
                "Company": "Acme",
                "Location": "Monterrey",
                "Url": "https://www.linkedin.com/jobs/view/1234567891",
                "Remote": "REMOTE",
                "JobID": "1234567891",
            },
        ]
    )
    detailed_jobs = pd.DataFrame(
        [
            {
                "Title": "Data Scientist",
                "Company": "Acme",
                "Location": "Monterrey",
                "Remote": "REMOTE",
                "Url": "https://www.linkedin.com/jobs/view/1234567890",
                "JobID": "1234567890",
                "SeniorityLevel": "Entry level",
                "EmploymentType": "Full-time",
                "JobFunction": "Research and Design",
                "Industries": "Technology",
                "PostedTime": "2 weeks ago",
                "NumApplicants": "Be among the first 25 applicants",
                "Description": "Build data products.",
            },
            {
                "Title": "Finance Analyst",
                "Company": "Acme",
                "Location": "Monterrey",
                "Remote": "REMOTE",
                "Url": "https://www.linkedin.com/jobs/view/1234567891",
                "JobID": "1234567891",
                "SeniorityLevel": "Entry level",
                "EmploymentType": "Full-time",
                "JobFunction": "Finance",
                "Industries": "Technology",
                "PostedTime": "2 weeks ago",
                "NumApplicants": "Over 200 applicants",
                "Description": "Analyze budgets.",
            },
        ]
    )
    fake_job_scraper = FakeJobScraper(scraped_jobs, detailed_jobs)
    fake_cleaner = FakeCleaner()
    config = JobScraperConfig(
        position="Data Scientist",
        location="Monterrey",
        advanced_config=JobScraperAdvancedConfig(KEYWORDS=["data scientist"]),
    )

    scraper = LinkedInJobScraper(
        logger=LOGGER,
        config=config,
        job_scraper=fake_job_scraper,
        job_data_cleaner=fake_cleaner,
    )

    jobs = scraper.run()

    assert fake_job_scraper.received_detail_jobs is not None
    assert fake_job_scraper.received_detail_jobs["JobID"].tolist() == ["1234567890"]
    assert fake_cleaner.location_mapping is None
    assert fake_cleaner.cleaned_detail_jobs is not None
    assert jobs["Title"].tolist() == ["Data Scientist"]
    assert jobs["DetailsCleaned"].tolist() == [True]
    assert "FinalProcessed" not in jobs.columns


def test_linkedin_job_scraper_returns_empty_frame_when_scrape_raises():
    scraper = LinkedInJobScraper(
        logger=LOGGER,
        config=JobScraperConfig(position="Data Scientist", location="Monterrey"),
        job_scraper=ExplodingJobScraper(),
        job_data_cleaner=FakeCleaner(),
    )

    jobs = scraper.run()

    assert jobs.empty
