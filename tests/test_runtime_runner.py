from __future__ import annotations

import logging
import shutil
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from linkedin_web_scraper.application.runtime_runner import RuntimeRunner
from linkedin_web_scraper.config.runtime import RuntimeConfig

TEST_TMP_ROOT = Path(".tmp") / "runtime-runner-tests"


class FakeStorage:
    init_calls: list[dict[str, object]] = []
    loaded_runs: list[str] = []

    def __init__(self, logger, *, storage_url):
        type(self).init_calls.append({"logger": logger, "storage_url": storage_url})
        self.engine = SimpleNamespace(dispose=lambda: type(self).init_calls.append({"disposed": True}))

    def load_run_jobs(self, run_id: str) -> pd.DataFrame:
        type(self).loaded_runs.append(run_id)
        return pd.DataFrame([{"JobID": "123", "Title": "Data Scientist"}])


class FakeDailyService:
    init_calls: list[dict[str, object]] = []
    once_calls: list[dict[str, object]] = []
    daily_calls: list[dict[str, object]] = []

    def __init__(self, logger, *, storage):
        type(self).init_calls.append({"logger": logger, "storage": storage})

    def run_for_location(self, **kwargs):
        type(self).once_calls.append(kwargs)
        return pd.DataFrame([{"JobID": "123"}])

    def run_daily(self, **kwargs):
        type(self).daily_calls.append(kwargs)
        return pd.DataFrame([{"JobID": "daily-123"}])


def _reset_directory(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_runtime_runner_run_once_uses_runtime_config_and_storage_url():
    FakeStorage.init_calls.clear()
    FakeDailyService.init_calls.clear()
    FakeDailyService.once_calls.clear()
    runner = RuntimeRunner(
        logger=logging.getLogger("runtime-runner-once"),
        daily_service_cls=FakeDailyService,
        storage_cls=FakeStorage,
    )
    runtime_config = RuntimeConfig()
    runtime_config.storage.url = "sqlite:///runtime.sqlite"
    runtime_config.scrape_once.position = "ML Engineer"
    runtime_config.scrape_once.location = "Austin"
    runtime_config.scrape_once.openai_enabled = True
    runtime_config.scrape_once.openai_model = "gpt-4.1-mini"
    runtime_config.scrape_once.file_name = "jobs.csv"

    result = runner.run_once(runtime_config)

    assert result["JobID"].tolist() == ["123"]
    assert FakeStorage.init_calls[0]["storage_url"] == "sqlite:///runtime.sqlite"
    assert FakeDailyService.once_calls[0]["position"] == "ML Engineer"
    assert FakeDailyService.once_calls[0]["location"] == "Austin"
    assert FakeDailyService.once_calls[0]["openai_enabled"] is True
    assert FakeDailyService.once_calls[0]["openai_model"] == "gpt-4.1-mini"
    assert FakeDailyService.once_calls[0]["file_name"] == "jobs.csv"


def test_runtime_runner_run_daily_uses_resolved_config_values():
    FakeStorage.init_calls.clear()
    FakeDailyService.daily_calls.clear()
    runner = RuntimeRunner(
        logger=logging.getLogger("runtime-runner-daily"),
        daily_service_cls=FakeDailyService,
        storage_cls=FakeStorage,
    )
    runtime_config = RuntimeConfig()
    runtime_config.scrape_daily.cities = ("Austin", "Dallas")
    runtime_config.scrape_daily.position = "ML Engineer"
    runtime_config.scrape_daily.openai_enabled = True
    runtime_config.scrape_daily.openai_model = "gpt-4o-mini"
    runtime_config.scrape_daily.combined_file_name = "combined.csv"

    result = runner.run_daily(runtime_config)

    assert result["JobID"].tolist() == ["daily-123"]
    assert FakeDailyService.daily_calls[0]["cities"] == ("Austin", "Dallas")
    assert FakeDailyService.daily_calls[0]["position"] == "ML Engineer"
    assert FakeDailyService.daily_calls[0]["openai_enabled"] is True
    assert FakeDailyService.daily_calls[0]["openai_model"] == "gpt-4o-mini"
    assert FakeDailyService.daily_calls[0]["combined_file_name"] == "combined.csv"


def test_runtime_runner_export_run_writes_csv():
    FakeStorage.init_calls.clear()
    FakeStorage.loaded_runs.clear()
    output_dir = _reset_directory(TEST_TMP_ROOT / "export")
    runner = RuntimeRunner(logger=logging.getLogger("runtime-runner-export"), storage_cls=FakeStorage)
    runtime_config = RuntimeConfig()
    runtime_config.storage.url = "sqlite:///runtime.sqlite"
    runtime_config.export.run_id = "run-123"
    runtime_config.export.file_name = "export.csv"
    runtime_config.export.output_dir = str(output_dir)

    output_path = runner.export_run(runtime_config)

    exported = pd.read_csv(output_path)

    assert Path(output_path).exists()
    assert FakeStorage.loaded_runs == ["run-123"]
    assert exported["JobID"].tolist() == [123]
    assert exported["Title"].tolist() == ["Data Scientist"]
