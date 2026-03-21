from __future__ import annotations

import pandas as pd

from linkedin_web_scraper.config import LOCATION_MAPPING, normalize_location_name
from linkedin_web_scraper.domain.job_data_cleaner import JobDataCleaner

MONTERREY_CITY = "San Pedro Garza Garc\u00eda"
MEXICO_CITY_BOROUGH = "\u00c1lvaro Obreg\u00f3n"


def test_location_mapping_uses_proper_unicode_keys():
    assert MONTERREY_CITY in LOCATION_MAPPING
    assert MEXICO_CITY_BOROUGH in LOCATION_MAPPING
    assert LOCATION_MAPPING[MONTERREY_CITY] == "Monterrey Metropolitan Area"


def test_location_normalization_repairs_mojibake():
    mojibake_name = "San Pedro Garza Garc\u00c3\u00ada"
    repaired_name = normalize_location_name(mojibake_name)

    assert repaired_name == MONTERREY_CITY
    assert LOCATION_MAPPING[repaired_name] == "Monterrey Metropolitan Area"


def test_location_normalization_handles_mexico_city_aliases():
    mojibake_name = "\u00c3\u0081lvaro Obreg\u00c3\u00b3n"
    repaired_name = normalize_location_name(mojibake_name)

    assert repaired_name == MEXICO_CITY_BOROUGH
    assert LOCATION_MAPPING[repaired_name] == "Mexico City Metropolitan Area"


def test_job_data_cleaner_repairs_mojibake_locations_and_preserves_job_id():
    cleaner = JobDataCleaner()
    df = pd.DataFrame(
        [
            {
                "Location": "San Pedro Garza Garc\u00c3\u00ada, Nuevo Leon, Mexico",
                "Title": "Data Scientist",
                "Company": "Example Co",
                "Url": "https://www.linkedin.com/jobs/view/1234567890?position=1&pageNum=0",
                "Remote": "Remote",
            }
        ]
    )

    cleaned = cleaner.clean_jobs_dataframe(df, LOCATION_MAPPING)

    assert cleaned.shape[0] == 1
    assert cleaned.iloc[0]["Location"] == "Monterrey Metropolitan Area"
    assert cleaned.iloc[0]["JobID"] == "1234567890"


def test_job_data_cleaner_handles_empty_frame_after_location_filter():
    cleaner = JobDataCleaner()
    df = pd.DataFrame(
        [
            {
                "Location": "Unmapped City, Example State, Mexico",
                "Title": "Data Scientist",
                "Company": "Example Co",
                "Url": "https://www.linkedin.com/jobs/view/1234567890?position=1&pageNum=0",
                "Remote": "Remote",
            }
        ]
    )

    cleaned = cleaner.clean_jobs_dataframe(df, LOCATION_MAPPING)

    assert cleaned.empty
    assert "JobID" in cleaned.columns