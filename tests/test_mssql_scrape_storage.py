"""Storage regression coverage against a real mssql server.

Skipped unless LINKEDIN_WEB_SCRAPER_TEST_MSSQL_URL points at a reachable mssql
instance (a mssql+pyodbc:// URL). CI supplies this via a
mcr.microsoft.com/mssql/server service container; locally it is opt-in.
"""

from __future__ import annotations

import os

import pandas as pd
import pytest

from linkedin_web_scraper.application.storage import ScrapeRunContext
from linkedin_web_scraper.infra.storage.models import Base
from linkedin_web_scraper.infra.storage.sqlite import SQLiteScrapeStorage

MSSQL_URL_ENV = "LINKEDIN_WEB_SCRAPER_TEST_MSSQL_URL"

pytestmark = pytest.mark.skipif(
    not os.environ.get(MSSQL_URL_ENV),
    reason=f"set {MSSQL_URL_ENV} to a mssql+pyodbc:// URL to run mssql storage tests",
)


def _fresh_storage() -> SQLiteScrapeStorage:
    storage = SQLiteScrapeStorage(storage_url=os.environ[MSSQL_URL_ENV])
    # Isolate this test run: a mssql instance is one shared database, not a
    # throwaway file like the sqlite tests get, so reset the schema first.
    Base.metadata.drop_all(storage.engine)
    Base.metadata.create_all(storage.engine)
    return storage


def test_mssql_storage_persists_run_and_jobs():
    storage = _fresh_storage()
    try:
        context = ScrapeRunContext(
            position="Data Scientist",
            location="Monterrey",
            enrichment_provider="NONE",
            time_posted="DAY",
        )
        run_id = storage.begin_run(context)
        df_jobs = pd.DataFrame([{"JobID": "1", "Title": "Data Scientist", "Company": "Acme"}])
        storage.store_jobs(run_id, df_jobs)
        storage.finish_run(run_id, row_count=1)

        loaded = storage.load_run_jobs(run_id)
        assert loaded["JobID"].tolist() == ["1"]
    finally:
        storage.engine.dispose()


def test_mssql_storage_round_trips_spanish_unicode_text():
    storage = _fresh_storage()
    try:
        context = ScrapeRunContext(
            position="Cientifico de Datos",
            location="Ciudad de Mexico",
            enrichment_provider="NONE",
            time_posted="DAY",
        )
        run_id = storage.begin_run(context)
        description = (
            "Disenar modelos de aprendizaje automatico: nino, manana, jalapeno con enie -> niño"
        )
        df_jobs = pd.DataFrame(
            [
                {
                    "JobID": "2",
                    "Title": "Ingeniero de Aprendizaje Automatico",
                    "Company": "Compañia Española",
                    "ShortDescription": description,
                }
            ]
        )
        storage.store_jobs(run_id, df_jobs)

        loaded = storage.load_run_jobs(run_id)
        assert loaded["Title"].tolist() == ["Ingeniero de Aprendizaje Automatico"]
        assert loaded["Company"].tolist() == ["Compañia Española"]
        assert loaded["ShortDescription"].tolist()[0] == description
    finally:
        storage.engine.dispose()
