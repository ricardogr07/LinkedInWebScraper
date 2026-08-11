"""SQLAlchemy-backed storage adapter for persisted scrape runs.

Despite the name, this works against any SQLAlchemy-supported dialect (SQLite by
default, or mssql via a mssql+pyodbc:// storage_url), not only SQLite. The class
keeps its original name because renaming it is a public-contract break with no
acceptance-criteria benefit; a rename is a bigger, riskier diff than the fix this
issue asks for.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, delete, inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from linkedin_web_scraper.application.storage import ScrapeRunContext, ScrapeStorage
from linkedin_web_scraper.config.storage import build_sqlite_storage_url
from linkedin_web_scraper.infra.logging import Logger, resolve_logger
from linkedin_web_scraper.infra.openai.models import NOT_AVAILABLE
from linkedin_web_scraper.infra.storage.models import (
    Base,
    JobEnrichmentRecord,
    JobRecord,
    JobSnapshotRecord,
    ScrapeRunRecord,
    utcnow,
)

ENRICHMENT_COLUMNS = (
    "ShortDescription",
    "TechStack",
    "YoE",
    "MinLevelStudies",
    "English",
    "EnrichmentModel",
    "EnrichmentResponseId",
    "EnrichmentRawPayload",
)

# Legacy sqlite column names from before the openai-to-enrichment rename, keyed
# by table name. Scoped strictly to this known rename, not a migration framework.
_LEGACY_COLUMN_RENAMES: dict[str, dict[str, str]] = {
    "scrape_runs": {"openai_enabled": "enrichment_provider"},
    "job_enrichments": {
        "openai_model": "enrichment_model",
        "openai_response_id": "enrichment_response_id",
    },
}


def _migrate_legacy_columns(engine: Engine) -> None:
    """Rename pre-rename legacy columns in place, if an old schema is found."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table_name, renames in _LEGACY_COLUMN_RENAMES.items():
            if table_name not in existing_tables:
                continue
            existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
            for old_name, new_name in renames.items():
                if old_name in existing_columns and new_name not in existing_columns:
                    connection.execute(
                        text(f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}")
                    )


class SQLiteScrapeStorage(ScrapeStorage):
    """Persist scrape runs, job snapshots, and enrichments (SQLite or mssql)."""

    def __init__(
        self,
        logger: logging.Logger | Logger | None = None,
        *,
        storage_url: str | None = None,
        engine: Engine | None = None,
    ):
        self.logger = resolve_logger(logger, name=__name__)
        self.storage_url = storage_url or build_sqlite_storage_url()
        # pool_pre_ping: cheap SELECT 1 before reuse so a stale connection (e.g. an
        # Azure SQL serverless tier resuming from auto-pause) is replaced, not surfaced
        # as an OperationalError mid-query.
        self.engine = engine or create_engine(self.storage_url, future=True, pool_pre_ping=True)
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False)
        _migrate_legacy_columns(self.engine)
        Base.metadata.create_all(self.engine)

    def begin_run(self, context: ScrapeRunContext) -> str:
        """Create a persisted scrape run and return its run identifier."""
        run_id = str(uuid.uuid4())
        run_record = ScrapeRunRecord(
            id=run_id,
            position=context.position,
            location=context.location,
            enrichment_provider=context.enrichment_provider,
            time_posted=context.time_posted,
            remote_types_json=json.dumps(list(context.remote_types), ensure_ascii=True),
            output_path=context.output_path,
            extra_metadata_json=json.dumps(context.metadata, ensure_ascii=True),
        )

        with self.session_factory.begin() as session:
            session.add(run_record)

        self.logger.info("Created persisted scrape run %s.", run_id)
        return run_id

    def store_jobs(self, run_id: str, df_jobs: pd.DataFrame) -> None:
        """Persist the dataframe rows for a scrape run."""
        if df_jobs.empty:
            self.logger.info("Run %s produced no jobs to persist.", run_id)
            return

        now = utcnow()
        records: list[dict[str, Any]] = []
        seen_job_ids: set[str] = set()
        duplicate_count = 0

        for snapshot_order, record in enumerate(df_jobs.to_dict(orient="records")):
            row = self._normalize_row(record)
            job_id = self._extract_job_id(row, run_id=run_id, snapshot_order=snapshot_order)
            if job_id in seen_job_ids:
                duplicate_count += 1
                continue
            seen_job_ids.add(job_id)
            records.append(row)

        with self.session_factory.begin() as session:
            session.execute(delete(JobSnapshotRecord).where(JobSnapshotRecord.run_id == run_id))
            session.execute(delete(JobEnrichmentRecord).where(JobEnrichmentRecord.run_id == run_id))

            for snapshot_order, row in enumerate(records):
                job_id = self._extract_job_id(row, run_id=run_id, snapshot_order=snapshot_order)
                self._upsert_job_record(session, job_id=job_id, row=row, now=now)
                session.add(
                    JobSnapshotRecord(
                        run_id=run_id,
                        job_id=job_id,
                        snapshot_order=snapshot_order,
                        title=self._stringify(row.get("Title")),
                        company=self._stringify(row.get("Company")),
                        location=self._stringify(row.get("Location")),
                        remote=self._stringify(row.get("Remote")),
                        url=self._stringify(row.get("Url")),
                        row_json=json.dumps(row, ensure_ascii=True),
                    )
                )

                enrichment_record = self._build_enrichment_record(
                    run_id=run_id, job_id=job_id, row=row
                )
                if enrichment_record is not None:
                    session.add(enrichment_record)

        if duplicate_count:
            self.logger.info(
                "Skipped %s duplicate job snapshots for run %s.", duplicate_count, run_id
            )
        self.logger.info("Persisted %s jobs for run %s.", len(records), run_id)

    def load_run_jobs(self, run_id: str) -> pd.DataFrame:
        """Load the persisted dataframe rows for one scrape run."""
        with self.session_factory() as session:
            snapshots = session.execute(
                select(JobSnapshotRecord.row_json)
                .where(JobSnapshotRecord.run_id == run_id)
                .order_by(JobSnapshotRecord.snapshot_order.asc())
            ).scalars()
            records = [json.loads(row_json) for row_json in snapshots]

        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)

    def finish_run(
        self,
        run_id: str,
        *,
        status: str = "completed",
        output_path: str | None = None,
        error_message: str | None = None,
        row_count: int | None = None,
    ) -> None:
        """Mark a persisted scrape run as finished."""
        with self.session_factory.begin() as session:
            run_record = session.get(ScrapeRunRecord, run_id)
            if run_record is None:
                raise KeyError(f"Unknown scrape run id: {run_id}")

            run_record.status = status
            run_record.output_path = output_path or run_record.output_path
            run_record.error_message = error_message
            run_record.row_count = row_count if row_count is not None else run_record.row_count
            run_record.finished_at = utcnow()

        self.logger.info("Marked scrape run %s as %s.", run_id, status)

    def _upsert_job_record(
        self,
        session: Session,
        *,
        job_id: str,
        row: dict[str, Any],
        now: datetime,
    ) -> None:
        job_record = session.get(JobRecord, job_id)
        if job_record is None:
            session.add(
                JobRecord(
                    job_id=job_id,
                    title=self._stringify(row.get("Title")),
                    company=self._stringify(row.get("Company")),
                    location=self._stringify(row.get("Location")),
                    url=self._stringify(row.get("Url")),
                    first_seen_at=now,
                    last_seen_at=now,
                )
            )
            return

        job_record.title = self._stringify(row.get("Title"))
        job_record.company = self._stringify(row.get("Company"))
        job_record.location = self._stringify(row.get("Location"))
        job_record.url = self._stringify(row.get("Url"))
        job_record.last_seen_at = now

    def _build_enrichment_record(
        self,
        *,
        run_id: str,
        job_id: str,
        row: dict[str, Any],
    ) -> JobEnrichmentRecord | None:
        if not any(column in row for column in ENRICHMENT_COLUMNS):
            return None

        values = {column: row.get(column) for column in ENRICHMENT_COLUMNS}
        if all(value in (None, "", NOT_AVAILABLE) for value in values.values()):
            return None

        english_value = values.get("English")
        if isinstance(english_value, bool):
            english_text = str(english_value)
        else:
            english_text = self._stringify(english_value)

        return JobEnrichmentRecord(
            run_id=run_id,
            job_id=job_id,
            short_description=self._stringify(values.get("ShortDescription")),
            tech_stack=self._stringify(values.get("TechStack")),
            years_of_experience=self._stringify(values.get("YoE")),
            minimum_level_of_studies=self._stringify(values.get("MinLevelStudies")),
            english_requirement=english_text,
            enrichment_model=self._stringify(values.get("EnrichmentModel")),
            enrichment_response_id=self._stringify(values.get("EnrichmentResponseId")),
            raw_payload_json=self._stringify(values.get("EnrichmentRawPayload")),
        )

    @staticmethod
    def _normalize_row(row: Mapping[object, Any]) -> dict[str, Any]:
        return {str(key): SQLiteScrapeStorage._normalize_value(value) for key, value in row.items()}

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if value is None:
            return None

        try:
            if pd.isna(value):
                return None
        except TypeError:
            pass

        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, (bool, int, float, str)):
            return value
        return str(value)

    @staticmethod
    def _extract_job_id(row: dict[str, Any], *, run_id: str, snapshot_order: int) -> str:
        job_id = str(row.get("JobID") or "").strip()
        if job_id:
            row["JobID"] = job_id
            return job_id
        return f"{run_id}-snapshot-{snapshot_order}"

    @staticmethod
    def _stringify(value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value)


__all__ = ["ENRICHMENT_COLUMNS", "SQLiteScrapeStorage"]
