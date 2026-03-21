from __future__ import annotations

import shutil
from pathlib import Path

from linkedin_web_scraper.config.options import RemoteType, TimePosted
from linkedin_web_scraper.config.runtime import load_runtime_config

TEST_TMP_ROOT = Path(".tmp") / "runtime-config-tests"


def _reset_directory(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_load_runtime_config_reads_toml_sections():
    tmp_dir = _reset_directory(TEST_TMP_ROOT / "toml-load")
    config_path = tmp_dir / "runtime.toml"
    config_path.write_text(
        """
[logging]
level = "debug"
file_name = "cli.log"

[storage]
file_name = "jobs.sqlite"
state_dir = "state"

[scrape.once]
position = "ML Engineer"
location = "Austin"
openai_enabled = true
openai_model = "gpt-4o-mini"
time_posted = "week"
remote_types = ["remote", "hybrid"]
file_name = "once.csv"
output_dir = "jobs"
append = false

[scrape.daily]
cities = ["Austin", "Dallas"]
position = "ML Engineer"
openai_enabled = true
openai_model = "gpt-4.1-mini"
time_posted = "day"
output_dir = "daily-jobs"
combined_file_name = "daily.csv"

[export]
run_id = "run-123"
file_name = "export.csv"
output_dir = "exports"
""",
        encoding="utf-8",
    )

    runtime_config = load_runtime_config(config_path)

    assert runtime_config.logging.level == "DEBUG"
    assert runtime_config.logging.file_name == "cli.log"
    assert runtime_config.storage.file_name == "jobs.sqlite"
    assert runtime_config.storage.state_dir == "state"
    assert runtime_config.scrape_once.position == "ML Engineer"
    assert runtime_config.scrape_once.location == "Austin"
    assert runtime_config.scrape_once.openai_enabled is True
    assert runtime_config.scrape_once.time_posted == TimePosted.WEEK
    assert runtime_config.scrape_once.remote_types == (RemoteType.REMOTE, RemoteType.HYBRID)
    assert runtime_config.scrape_once.append is False
    assert runtime_config.scrape_daily.cities == ("Austin", "Dallas")
    assert runtime_config.scrape_daily.openai_model == "gpt-4.1-mini"
    assert runtime_config.export.run_id == "run-123"
    assert runtime_config.export.file_name == "export.csv"


def test_load_runtime_config_applies_environment_overrides():
    tmp_dir = _reset_directory(TEST_TMP_ROOT / "env-overrides")
    config_path = tmp_dir / "runtime.toml"
    config_path.write_text(
        """
[logging]
level = "INFO"
file_name = "main.log"

[storage]
file_name = "jobs.sqlite"

[scrape.once]
position = "Data Scientist"
location = "Monterrey"
""",
        encoding="utf-8",
    )

    runtime_config = load_runtime_config(
        config_path,
        environ={
            "LINKEDIN_WEB_SCRAPER_LOG_LEVEL": "warning",
            "LINKEDIN_WEB_SCRAPER_STORAGE_URL": "sqlite:///override.sqlite",
            "LINKEDIN_WEB_SCRAPER_OUTPUT_DIR": "custom-output",
            "LINKEDIN_WEB_SCRAPER_OPENAI_ENABLED": "true",
            "LINKEDIN_WEB_SCRAPER_OPENAI_MODEL": "gpt-4.1-mini",
        },
    )

    assert runtime_config.logging.level == "WARNING"
    assert runtime_config.storage.url == "sqlite:///override.sqlite"
    assert runtime_config.scrape_once.output_dir == "custom-output"
    assert runtime_config.scrape_daily.output_dir == "custom-output"
    assert runtime_config.export.output_dir == "custom-output"
    assert runtime_config.scrape_once.openai_enabled is True
    assert runtime_config.scrape_daily.openai_enabled is True
    assert runtime_config.scrape_once.openai_model == "gpt-4.1-mini"
    assert runtime_config.scrape_daily.openai_model == "gpt-4.1-mini"
