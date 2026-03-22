from __future__ import annotations

from pathlib import Path

from linkedin_web_scraper.application.release_manager import (
    build_release_gate,
    parse_version_tuple,
    read_project_version,
    release_tag,
)


def test_release_tag_prefixes_versions_with_v() -> None:
    assert release_tag("1.1.1") == "v1.1.1"
    assert release_tag("v1.1.1") == "v1.1.1"


def test_parse_version_tuple_supports_partial_numeric_versions() -> None:
    assert parse_version_tuple("1") == (1, 0, 0)
    assert parse_version_tuple("1.2") == (1, 2, 0)
    assert parse_version_tuple("1.1.1") == (1, 1, 1)


def test_build_release_gate_allows_bumped_version_when_checks_pass() -> None:
    gate = build_release_gate(
        "1.1.1",
        "1.1.0",
        ci_success=True,
        docs_success=True,
        release_exists=False,
    )

    assert gate.should_auto_release is True
    assert gate.release_tag == "v1.1.1"


def test_build_release_gate_tolerates_legacy_latest_release_version() -> None:
    gate = build_release_gate(
        "1.1.1",
        "1",
        ci_success=True,
        docs_success=True,
        release_exists=False,
    )

    assert gate.should_auto_release is True
    assert gate.latest_released_version == "1"


def test_build_release_gate_blocks_duplicate_and_non_bumped_releases() -> None:
    duplicate_gate = build_release_gate(
        "1.1.1",
        "1.1.0",
        ci_success=True,
        docs_success=True,
        release_exists=True,
    )
    stale_gate = build_release_gate(
        "1.1.0",
        "1.1.0",
        ci_success=True,
        docs_success=True,
        release_exists=False,
    )

    assert duplicate_gate.should_auto_release is False
    assert "already exists" in duplicate_gate.reason
    assert stale_gate.should_auto_release is False
    assert "not newer" in stale_gate.reason


def test_read_project_version_reads_version_from_toml(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "2.3.4"\n', encoding="utf-8")

    assert read_project_version(pyproject) == "2.3.4"
