from __future__ import annotations

from datetime import datetime

import pandas as pd

import linkedin_web_scraper.domain.job_data_cleaner as cleaner_module
from linkedin_web_scraper.domain.job_data_cleaner import JobDataCleaner


class FrozenDateTime(datetime):
    @classmethod
    def today(cls) -> datetime:
        return cls(2026, 3, 21)


def test_clean_extracted_job_data_normalizes_detail_fields(monkeypatch):
    monkeypatch.setattr(cleaner_module, "datetime", FrozenDateTime)
    cleaner = JobDataCleaner()
    df_jobs = pd.DataFrame(
        [
            {
                "Title": "Data Scientist",
                "Company": "Acme Corp",
                "Location": "Monterrey Metropolitan Area",
                "Remote": "REMOTE",
                "SeniorityLevel": "Not Applicable",
                "EmploymentType": "Full-time",
                "Industries": "Technology",
                "PostedTime": "2 weeks ago",
                "NumApplicants": "Be among the first 25 applicants",
                "JobFunction": "Research and Design",
                "Description": "Build production data pipelines.",
                "Url": "https://www.linkedin.com/jobs/view/1234567890",
                "JobID": "1234567890",
            }
        ]
    )

    cleaned = cleaner.clean_extracted_job_data(df_jobs)

    assert list(cleaned.columns) == [
        "Title",
        "Company",
        "Location",
        "Remote",
        "SeniorityLevel",
        "EmploymentType",
        "Industries",
        "DatePosted",
        "NumApplicants",
        "JobFunction1",
        "JobFunction2",
        "JobFunction3",
        "Description",
        "Url",
        "JobID",
    ]
    assert cleaned.iloc[0]["SeniorityLevel"] == "N/A"
    assert cleaned.iloc[0]["NumApplicants"] == 25
    assert cleaned.iloc[0]["JobFunction1"] == "R&D"
    assert cleaned.iloc[0]["JobFunction2"] == "N/A"
    assert cleaned.iloc[0]["JobFunction3"] == "N/A"
    assert cleaned.iloc[0]["DatePosted"] == FrozenDateTime(2026, 3, 7)
    assert str(cleaned["EmploymentType"].dtype) == "category"


def test_process_enriched_job_data_derives_experience_studies_and_tech_stack():
    cleaner = JobDataCleaner()
    df_jobs = pd.DataFrame(
        [
            {
                "YoE": "3+ years of experience",
                "MinLevelStudies": "Bachelor's degree in Computer Science",
                "TechStack": "Python, SQL",
            },
            {
                "YoE": "N/A",
                "MinLevelStudies": "Master of Science",
                "TechStack": "Terraform",
            },
        ]
    )

    processed = cleaner.process_enriched_job_data(
        df_jobs,
        {"Languages": ["Python", "SQL"], "Cloud": ["AWS"]},
    )

    assert processed["MinYoE"].tolist() == [3, "N/A"]
    assert processed["MinLevelStudies"].tolist() == ["Bachelor", "Masters"]
    assert processed["Languages"].tolist() == [1, 0]
    assert processed["Cloud"].tolist() == [0, 0]
    assert processed["Other"].tolist() == [0, 1]
