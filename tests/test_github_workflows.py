"""Regression coverage for the tracked GitHub workflow assets."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
RUNTIME_DIR = REPO_ROOT / ".github" / "runtime"
TOX_FILE = REPO_ROOT / "tox.toml"


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

    missing = sorted(
        str(path.relative_to(REPO_ROOT)) for path in expected_files if not path.exists()
    )
    assert not missing, f"Missing workflow assets: {missing}"


def test_ci_workflow_uses_tox_matrix_and_canonical_smoke() -> None:
    text = _read(".github/workflows/ci.yml")
    assert "branches-ignore:" in text
    assert "- data" in text
    assert "python -m tox -e" in text
    assert "py311" in text
    assert "py314" in text
    assert "smoke" in text
    assert "python -m tox -e smoke" in text
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


def test_release_workflow_uses_auto_release_and_trusted_publishing() -> None:
    text = _read(".github/workflows/release.yml")
    assert "workflow_run:" in text
    assert "workflow_dispatch:" in text
    assert "- CI" in text
    assert "- Docs" in text
    assert "contents: write" in text
    assert "actions: read" in text
    assert "pypa/gh-action-pypi-publish@release/v1" in text
    assert "id-token: write" in text
    assert "softprops/action-gh-release@v2" in text
    assert "tag_name:" in text
    assert "target_commitish:" in text
    assert "publish_pypi" in text
    assert "testpypi" not in text


def test_daily_workflow_persists_release_state_and_artifacts() -> None:
    text = _read(".github/workflows/daily-scrape.yml")
    assert "schedule:" in text
    assert "git worktree add --orphan -b data .tmp/data-branch" in text
    assert ".github/runtime/daily.toml" in text
    assert "gh release download data-latest" in text
    assert "gh release upload data-latest artifacts/state/linkedin_jobs.sqlite --clobber" in text
    # a scheduled run must never fresh-start; only an explicit dispatch input may
    assert "allow_fresh_state" in text
    assert "Refusing to start fresh" in text
    assert "git add exports" in text
    assert "git add state" not in text
    assert "actions/setup-python@v7" in text
    assert "actions/upload-artifact@v7" in text
    assert "actions/github-script@v9" in text
    assert "[automation] Daily scrape failure" in text


def test_daily_runtime_config_is_valid_and_uses_managed_paths() -> None:
    config = tomllib.loads(_read(".github/runtime/daily.toml"))
    assert config["storage"]["state_dir"] == "artifacts/state"
    assert config["scrape"]["daily"]["enrichment_provider"] == "openai"
    assert config["scrape"]["daily"]["output_dir"] == "artifacts/jobs"
    assert config["logging"]["file_name"] == "daily-github-actions.log"


def test_tox_config_exposes_smoke_and_preflight() -> None:
    config = tomllib.loads(TOX_FILE.read_text(encoding="utf-8"))

    assert "smoke" in config["env_list"]
    assert "preflight" in config["env_list"]
    assert config["env"]["smoke"]["commands"][0][0] == "pytest"
    assert config["env"]["preflight"]["deps"][0] == "build>=1.2.2"
    assert config["env"]["preflight"]["commands"][0][0] == "pytest"
    assert config["env"]["preflight"]["commands"][-1][0] == "python"
