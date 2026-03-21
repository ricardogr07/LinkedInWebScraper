from __future__ import annotations

import os
from pathlib import Path

DEFAULT_ARTIFACTS_DIR = Path("artifacts")
DEFAULT_JOBS_OUTPUT_DIR = DEFAULT_ARTIFACTS_DIR / "jobs"
DEFAULT_LOGS_DIR = DEFAULT_ARTIFACTS_DIR / "logs"
DEFAULT_STATE_DIR = DEFAULT_ARTIFACTS_DIR / "state"


def _resolve_managed_path(
    file_name: str | Path,
    managed_dir: str | Path,
) -> str:
    """Resolve bare file names under a managed directory and preserve explicit paths."""
    candidate = Path(file_name)

    if candidate.is_absolute() or candidate.parent != Path("."):
        candidate.parent.mkdir(parents=True, exist_ok=True)
        return str(candidate)

    target_dir = Path(managed_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    return str(target_dir / candidate.name)


def resolve_jobs_output_path(
    file_name: str | Path,
    output_dir: str | Path | None = None,
) -> str:
    """Resolve a jobs CSV path under the managed jobs artifact directory by default."""
    return _resolve_managed_path(file_name, output_dir or DEFAULT_JOBS_OUTPUT_DIR)


def resolve_log_path(
    file_name: str | Path,
    log_dir: str | Path | None = None,
) -> str:
    """Resolve a log file path under the managed logs artifact directory by default."""
    if str(file_name).lower() == os.devnull.lower():
        return str(file_name)

    return _resolve_managed_path(file_name, log_dir or DEFAULT_LOGS_DIR)


def resolve_state_path(
    file_name: str | Path,
    state_dir: str | Path | None = None,
) -> str:
    """Resolve a state or database path under the managed state directory by default."""
    return _resolve_managed_path(file_name, state_dir or DEFAULT_STATE_DIR)


__all__ = [
    "DEFAULT_ARTIFACTS_DIR",
    "DEFAULT_JOBS_OUTPUT_DIR",
    "DEFAULT_LOGS_DIR",
    "DEFAULT_STATE_DIR",
    "resolve_jobs_output_path",
    "resolve_log_path",
    "resolve_state_path",
]
