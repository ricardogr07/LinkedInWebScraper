"""SQLAlchemy models for persisted scrape runs and job snapshots."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative model for the SQLite scrape storage schema."""


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp for persisted records."""
    return datetime.now(UTC)


class ScrapeRunRecord(Base):
    """Persist one application-level scrape run."""

    __tablename__ = "scrape_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    openai_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    time_posted: Mapped[str] = mapped_column(String(32), nullable=False)
    remote_types_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    output_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class JobRecord(Base):
    """Persist the latest known canonical attributes for one job ID."""

    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class JobSnapshotRecord(Base):
    """Persist one job row as it appeared in a specific scrape run."""

    __tablename__ = "job_snapshots"
    __table_args__ = (UniqueConstraint("run_id", "job_id", name="uq_job_snapshot_run_job"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    snapshot_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remote: Mapped[str | None] = mapped_column(String(64), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    row_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class JobEnrichmentRecord(Base):
    """Persist the structured OpenAI enrichment values for one run and job."""

    __tablename__ = "job_enrichments"
    __table_args__ = (UniqueConstraint("run_id", "job_id", name="uq_job_enrichment_run_job"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    short_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_of_experience: Mapped[str | None] = mapped_column(Text, nullable=True)
    minimum_level_of_studies: Mapped[str | None] = mapped_column(Text, nullable=True)
    english_requirement: Mapped[str | None] = mapped_column(String(32), nullable=True)
    openai_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    openai_response_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    raw_payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


__all__ = [
    "Base",
    "JobEnrichmentRecord",
    "JobRecord",
    "JobSnapshotRecord",
    "ScrapeRunRecord",
    "utcnow",
]
