from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from linkedin_web_scraper.application.storage import ScrapeRunContext
from linkedin_web_scraper.config.storage import build_sqlite_storage_url
from linkedin_web_scraper.infra.storage.sqlite import SQLiteScrapeStorage

TEST_TMP_ROOT = Path(".tmp") / "sqlite-storage-tests"


def _reset_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_sqlite_scrape_storage_persists_run_snapshots_and_enrichments():
    state_dir = _reset_directory(TEST_TMP_ROOT / "persisted-run")
    database_path = state_dir / "jobs.sqlite"
    if database_path.exists():
        database_path.unlink()

    storage = SQLiteScrapeStorage(
        storage_url=build_sqlite_storage_url(database_path.name, state_dir=state_dir)
    )
    context = ScrapeRunContext(
        position="Data Scientist",
        location="Monterrey",
        enrichment_provider="OPENAI",
        time_posted="DAY",
        remote_types=("REMOTE", "HYBRID"),
        output_path="artifacts/jobs/test.csv",
        metadata={"source": "test"},
    )
    df_jobs = pd.DataFrame(
        [
            {
                "JobID": "1234567890",
                "Title": "Data Scientist",
                "Company": "Acme",
                "Location": "Monterrey",
                "Remote": "REMOTE",
                "Url": "https://example.com/jobs/1234567890",
                "Description": "Build ML pipelines.",
                "ShortDescription": "Build ML pipelines and deploy models.",
                "TechStack": "Python, SQL",
                "YoE": "3+ years",
                "MinLevelStudies": "Bachelor",
                "English": True,
                "EnrichmentModel": "gpt-4o-mini",
                "EnrichmentResponseId": "resp_123",
                "EnrichmentRawPayload": '{"description": "Build ML pipelines and deploy models."}',
            },
            {
                "JobID": "1234567891",
                "Title": "ML Engineer",
                "Company": "Beta",
                "Location": "Monterrey",
                "Remote": "HYBRID",
                "Url": "https://example.com/jobs/1234567891",
                "Description": "Ship ML services.",
            },
        ]
    )

    run_id = storage.begin_run(context)
    storage.store_jobs(run_id, df_jobs)
    storage.finish_run(run_id, output_path=context.output_path, row_count=2)

    loaded = storage.load_run_jobs(run_id)

    assert loaded["JobID"].tolist() == ["1234567890", "1234567891"]
    assert loaded["ShortDescription"].tolist()[0] == "Build ML pipelines and deploy models."
    assert loaded["English"].tolist()[0] is True

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("select count(*) from scrape_runs").fetchone()[0] == 1
        assert connection.execute("select count(*) from jobs").fetchone()[0] == 2
        assert connection.execute("select count(*) from job_snapshots").fetchone()[0] == 2
        assert connection.execute("select count(*) from job_enrichments").fetchone()[0] == 1

        status, row_count, output_path = connection.execute(
            "select status, row_count, output_path from scrape_runs where id = ?",
            (run_id,),
        ).fetchone()

    assert status == "completed"
    assert row_count == 2
    assert output_path == "artifacts/jobs/test.csv"

    storage.engine.dispose()


def test_sqlite_scrape_storage_returns_empty_frame_for_runs_without_snapshots():
    state_dir = _reset_directory(TEST_TMP_ROOT / "empty-run")
    database_path = state_dir / "empty.sqlite"
    if database_path.exists():
        database_path.unlink()

    storage = SQLiteScrapeStorage(
        storage_url=build_sqlite_storage_url(database_path.name, state_dir=state_dir)
    )
    run_id = storage.begin_run(
        ScrapeRunContext(
            position="Data Scientist",
            location="Monterrey",
            enrichment_provider="NONE",
            time_posted="DAY",
        )
    )

    loaded = storage.load_run_jobs(run_id)

    assert loaded.empty

    storage.engine.dispose()


def test_sqlite_scrape_storage_deduplicates_duplicate_job_ids_within_one_run():
    state_dir = _reset_directory(TEST_TMP_ROOT / "duplicate-jobs")
    database_path = state_dir / "duplicate.sqlite"
    if database_path.exists():
        database_path.unlink()

    storage = SQLiteScrapeStorage(
        storage_url=build_sqlite_storage_url(database_path.name, state_dir=state_dir)
    )
    run_id = storage.begin_run(
        ScrapeRunContext(
            position="Data Scientist",
            location="Monterrey",
            enrichment_provider="NONE",
            time_posted="DAY",
        )
    )
    df_jobs = pd.DataFrame(
        [
            {"JobID": "1234567890", "Title": "Data Scientist", "Company": "Acme"},
            {"JobID": "1234567890", "Title": "Data Scientist", "Company": "Acme"},
        ]
    )

    storage.store_jobs(run_id, df_jobs)
    loaded = storage.load_run_jobs(run_id)

    assert loaded["JobID"].tolist() == ["1234567890"]

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("select count(*) from job_snapshots").fetchone()[0] == 1
        assert connection.execute("select count(*) from jobs").fetchone()[0] == 1

    storage.engine.dispose()
