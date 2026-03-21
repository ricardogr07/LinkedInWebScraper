from __future__ import annotations

from io import StringIO

import pandas as pd

from linkedin_web_scraper.config.job_scraper_advanced_config import JobScraperAdvancedConfig
from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
from linkedin_web_scraper.config.options import RemoteType, TimePosted
from linkedin_web_scraper.domain.job_data_cleaner import JobDataCleaner
from linkedin_web_scraper.infra.logging import configure_logging


def test_job_scraper_config_normalizes_string_inputs():
    config = JobScraperConfig(
        position="  Data Scientist  ",
        location=" Monterrey ",
        time_posted="day",
        remote="remote",
    )

    assert config.position == "Data Scientist"
    assert config.location == "Monterrey"
    assert config.time_posted is TimePosted.DAY
    assert config.remote is RemoteType.REMOTE


def test_advanced_config_copies_mutable_inputs():
    keywords = ["python", "sql"]
    location_mapping = {"Monterrey": "MTY"}
    skills = {"Languages": ["Python"]}

    config = JobScraperAdvancedConfig(
        LOCATION_MAPPING=location_mapping,
        KEYWORDS=keywords,
        SKILLS_CATEGORIES=skills,
    )

    keywords.append("ml")
    location_mapping["Mexico City"] = "CDMX"
    skills["Languages"].append("SQL")

    assert config.KEYWORDS == ["python", "sql"]
    assert config.LOCATION_MAPPING == {"Monterrey": "MTY"}
    assert config.SKILLS_CATEGORIES == {"Languages": ["Python"]}


def test_job_data_cleaner_uses_passed_location_mapping():
    df = pd.DataFrame(
        {
            "Location": ["Monterrey, Nuevo Leon, Mexico"],
            "Title": ["Data Scientist"],
            "Company": ["Acme"],
            "Url": ["https://www.linkedin.com/jobs/view/1234567890?position=1"],
            "Remote": ["REMOTE"],
        }
    )
    cleaner = JobDataCleaner()

    cleaned = cleaner.clean_jobs_dataframe(df, {"Monterrey": "MTY"})

    assert cleaned.iloc[0]["Location"] == "MTY"
    assert cleaned.iloc[0]["JobID"] == "1234567890"


def test_configure_logging_supports_stream_only_configuration():
    stream = StringIO()
    logger = configure_logging(stream=stream, filename=None, force=True)

    logger.warning("phase3-check")

    assert "phase3-check" in stream.getvalue()

