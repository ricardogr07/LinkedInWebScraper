from __future__ import annotations

import shutil
from pathlib import Path

import linkedin_web_scraper.infra.paths as paths
from linkedin_web_scraper.infra.paths import resolve_jobs_output_path, resolve_log_path

TEST_TMP_ROOT = Path(".tmp") / "artifact-path-tests"


def _reset_directory(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_resolve_jobs_output_path_defaults_to_managed_directory(monkeypatch):
    managed_dir = _reset_directory(TEST_TMP_ROOT / "jobs")
    monkeypatch.setattr(paths, "DEFAULT_JOBS_OUTPUT_DIR", managed_dir)

    resolved = resolve_jobs_output_path("jobs.csv")

    assert resolved == str(managed_dir / "jobs.csv")
    assert managed_dir.exists()

    shutil.rmtree(managed_dir)


def test_resolve_jobs_output_path_preserves_explicit_relative_parent():
    explicit_path = TEST_TMP_ROOT / "nested" / "jobs.csv"
    if explicit_path.parent.exists():
        shutil.rmtree(explicit_path.parent)

    resolved = resolve_jobs_output_path(explicit_path)

    assert resolved == str(explicit_path)
    assert explicit_path.parent.exists()

    shutil.rmtree(explicit_path.parent)


def test_resolve_log_path_defaults_to_managed_directory(monkeypatch):
    managed_dir = _reset_directory(TEST_TMP_ROOT / "logs")
    monkeypatch.setattr(paths, "DEFAULT_LOGS_DIR", managed_dir)

    resolved = resolve_log_path("main.log")

    assert resolved == str(managed_dir / "main.log")
    assert managed_dir.exists()

    shutil.rmtree(managed_dir)

