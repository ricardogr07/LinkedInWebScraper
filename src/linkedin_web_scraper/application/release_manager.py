"""Release gating helpers for automated GitHub Release and PyPI publishing."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

_VERSION_PATTERN = re.compile(r"^(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?$")


@dataclass(frozen=True, slots=True)
class ReleaseGate:
    """Resolved release gate state for a versioned release candidate."""

    current_version: str
    latest_released_version: str | None
    release_tag: str
    ci_success: bool
    docs_success: bool
    release_exists: bool
    should_auto_release: bool
    reason: str


def normalize_version_text(version_text: str) -> str:
    """Normalize a version string into the canonical ``X.Y.Z`` form."""
    normalized = str(version_text).strip()
    if normalized[:1].lower() == "v" and len(normalized) > 1 and normalized[1].isdigit():
        normalized = normalized[1:]
    return normalized


def parse_version_tuple(version_text: str) -> tuple[int, int, int]:
    """Parse a numeric version string into a sortable tuple."""
    normalized = normalize_version_text(version_text)
    match = _VERSION_PATTERN.fullmatch(normalized)
    if match is None:
        raise ValueError(f"Unsupported release version: {version_text!r}")
    major = int(match.group("major"))
    minor = int(match.group("minor") or 0)
    patch = int(match.group("patch") or 0)
    return (major, minor, patch)


def release_tag(version_text: str) -> str:
    """Return the Git tag name used for a release version."""
    return f"v{normalize_version_text(version_text)}"


def read_project_version(pyproject_path: str | Path = Path("pyproject.toml")) -> str:
    """Read the project version from ``pyproject.toml``."""
    project_path = Path(pyproject_path)
    data = tomllib.loads(project_path.read_text(encoding="utf-8"))
    project = data["project"]
    version = project["version"]
    return normalize_version_text(version)


def build_release_gate(
    current_version: str,
    latest_released_version: str | None,
    *,
    ci_success: bool,
    docs_success: bool,
    release_exists: bool,
) -> ReleaseGate:
    """Resolve whether an automated release should run for the current commit."""
    normalized_current = normalize_version_text(current_version)
    current_tuple = parse_version_tuple(normalized_current)
    normalized_latest = (
        normalize_version_text(latest_released_version)
        if latest_released_version is not None
        else None
    )
    latest_tuple = parse_version_tuple(normalized_latest) if normalized_latest is not None else None
    tag = release_tag(normalized_current)

    if not ci_success or not docs_success:
        return ReleaseGate(
            current_version=normalized_current,
            latest_released_version=normalized_latest,
            release_tag=tag,
            ci_success=ci_success,
            docs_success=docs_success,
            release_exists=release_exists,
            should_auto_release=False,
            reason="Waiting for both CI and Docs to complete successfully.",
        )

    if release_exists:
        return ReleaseGate(
            current_version=normalized_current,
            latest_released_version=normalized_latest,
            release_tag=tag,
            ci_success=ci_success,
            docs_success=docs_success,
            release_exists=release_exists,
            should_auto_release=False,
            reason=f"Release {tag} already exists.",
        )

    if latest_tuple is not None and current_tuple <= latest_tuple:
        return ReleaseGate(
            current_version=normalized_current,
            latest_released_version=normalized_latest,
            release_tag=tag,
            ci_success=ci_success,
            docs_success=docs_success,
            release_exists=release_exists,
            should_auto_release=False,
            reason=(
                f"Version {normalized_current} is not newer than the latest released "
                f"version {normalized_latest}."
            ),
        )

    return ReleaseGate(
        current_version=normalized_current,
        latest_released_version=normalized_latest,
        release_tag=tag,
        ci_success=ci_success,
        docs_success=docs_success,
        release_exists=release_exists,
        should_auto_release=True,
        reason=f"Version {normalized_current} is ready for an automated release.",
    )


__all__ = [
    "ReleaseGate",
    "build_release_gate",
    "normalize_version_text",
    "parse_version_tuple",
    "read_project_version",
    "release_tag",
]
