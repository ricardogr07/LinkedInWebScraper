"""Regression coverage for the tracked GitHub workflow assets."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
RUNTIME_DIR = REPO_ROOT / ".github" / "runtime"


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_required_workflow_files_exist() -> None:
    expected_files = {
        WORKFLOWS_DIR / "ci.yml",
        WORKFLOWS_DIR / "docs.yml",
        WORKFLOWS_DIR / "release.yml",
        WORKFLOWS_DIR / "daily-scrape.yml",
        RUNTIME_DIR / "daily.toml",
    }

    missing = sorted(str(path.relative_to(REPO_ROOT)) for path in expected_files if not path.exists())
    assert not missing, f"Missing workflow assets: {missing}"


def test_ci_workflow_uses_tox_matrix_and_canonical_smoke() -> None:
    text = _read(".github/workflows/ci.yml")
    assert "branches-ignore:" in text
    assert "- data" in text
    assert "python -m tox -e" in text
    assert "py311" in text
    assert "py314" in text
    assert "smoke" in text
    assert "tests/test_example_smoke.py" in text
    assert "tests/test_example_advanced_config_smoke.py" in text
    assert "tests/test_example_openai_smoke.py" in text
    assert "tests/test_main_smoke.py" in text
    assert "tests/test_process_ds_jobs_smoke.py" in text
    assert "lint" in text
    assert "type" in text
    assert "docs" in text
    assert "build" in text


def test_docs_workflow_deploys_pages() -> None:
    text = _read(".github/workflows/docs.yml")
    assert "branches:" in text
    assert "- main" in text
    assert "actions/configure-pages" in text
    assert "actions/upload-pages-artifact" in text
    assert "actions/deploy-pages" in text
    assert "mkdocs build --strict" in text


def test_release_workflow_uses_trusted_publishing() -> None:
    text = _read(".github/workflows/release.yml")
    assert "pypa/gh-action-pypi-publish@release/v1" in text
    assert "id-token: write" in text
    assert "testpypi" in text
    assert "pypi" in text


def test_daily_workflow_persists_state_branch_and_artifacts() -> None:
    text = _read(".github/workflows/daily-scrape.yml")
    assert "schedule:" in text
    assert "data" in text
    assert ".github/runtime/daily.toml" in text
    assert "actions/upload-artifact@v4" in text
    assert "[automation] Daily scrape failure" in text


def test_daily_runtime_config_is_valid_and_uses_managed_paths() -> None:
    config = tomllib.loads(_read(".github/runtime/daily.toml"))
    assert config["storage"]["state_dir"] == "artifacts/state"
    assert config["scrape"]["daily"]["output_dir"] == "artifacts/jobs"
    assert config["logging"]["file_name"] == "daily-github-actions.log"
