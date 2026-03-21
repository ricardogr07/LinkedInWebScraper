"""Storage-related runtime defaults and helpers."""

from __future__ import annotations

from pathlib import Path

from linkedin_web_scraper.infra.paths import resolve_state_path

DEFAULT_SQLITE_DB_FILE = "linkedin_jobs.sqlite"


def build_sqlite_storage_url(
    file_name: str | Path = DEFAULT_SQLITE_DB_FILE,
    state_dir: str | Path | None = None,
) -> str:
    """Build a SQLite URL rooted in the managed state directory by default."""
    database_path = Path(resolve_state_path(file_name, state_dir)).resolve()
    return f"sqlite:///{database_path.as_posix()}"


__all__ = ["DEFAULT_SQLITE_DB_FILE", "build_sqlite_storage_url"]
