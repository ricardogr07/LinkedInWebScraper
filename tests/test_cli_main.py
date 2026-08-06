from __future__ import annotations

import importlib
import sys
from io import StringIO

cli_main_module = importlib.import_module("linkedin_web_scraper.interfaces.cli.main")


class FakeRunner:
    describe_calls: list[str] = []
    run_daily_calls: list[object] = []
    run_once_calls: list[object] = []
    export_calls: list[object] = []

    def __init__(self, logger=None):
        self.logger = logger

    def describe_daily(self, runtime_config):
        type(self).describe_calls.append("daily")
        return {"command": "scrape daily", "cities": list(runtime_config.scrape_daily.cities)}

    def describe_once(self, runtime_config):
        type(self).describe_calls.append("once")
        return {"command": "scrape once", "position": runtime_config.scrape_once.position}

    def describe_export(self, runtime_config):
        type(self).describe_calls.append("export")
        return {"command": "export", "run_id": runtime_config.export.run_id}

    def run_daily(self, runtime_config):
        type(self).run_daily_calls.append(runtime_config)
        return None

    def run_once(self, runtime_config):
        type(self).run_once_calls.append(runtime_config)
        return None

    def export_run(self, runtime_config):
        type(self).export_calls.append(runtime_config)
        return None


def _reset_fake_runner() -> None:
    FakeRunner.describe_calls.clear()
    FakeRunner.run_daily_calls.clear()
    FakeRunner.run_once_calls.clear()
    FakeRunner.export_calls.clear()


def test_cli_main_defaults_to_daily_run():
    _reset_fake_runner()

    result = cli_main_module.main(
        [],
        runner_cls=FakeRunner,
        configure_logging_fn=lambda **kwargs: None,
        logger_factory=lambda name: object(),
    )

    assert result == 0
    assert len(FakeRunner.run_daily_calls) == 1
    assert FakeRunner.run_daily_calls[0].scrape_daily.position == "Data Scientist"


def test_cli_main_dry_run_prints_once_plan():
    _reset_fake_runner()
    output = StringIO()

    result = cli_main_module.main(
        ["scrape", "once", "--dry-run", "--position", "ML Engineer"],
        runner_cls=FakeRunner,
        configure_logging_fn=lambda **kwargs: None,
        logger_factory=lambda name: object(),
        stdout=output,
    )

    assert result == 0
    assert FakeRunner.describe_calls == ["once"]
    assert not FakeRunner.run_once_calls
    assert "scrape once" in output.getvalue()
    assert "ML Engineer" in output.getvalue()


def test_cli_main_reads_sys_argv_when_argv_is_none(monkeypatch):
    # The console script calls main() with argv=None; flags must not be discarded.
    _reset_fake_runner()
    output = StringIO()
    monkeypatch.setattr(
        sys,
        "argv",
        ["linkedin-webscraper", "scrape", "daily", "--dry-run", "--position", "ML Engineer"],
    )

    result = cli_main_module.main(
        None,
        runner_cls=FakeRunner,
        configure_logging_fn=lambda **kwargs: None,
        logger_factory=lambda name: object(),
        stdout=output,
    )

    assert result == 0
    assert FakeRunner.describe_calls == ["daily"]
    assert not FakeRunner.run_daily_calls
    assert "scrape daily" in output.getvalue()


def test_cli_main_export_command_uses_runner():
    _reset_fake_runner()

    result = cli_main_module.main(
        ["export", "--run-id", "run-123"],
        runner_cls=FakeRunner,
        configure_logging_fn=lambda **kwargs: None,
        logger_factory=lambda name: object(),
    )

    assert result == 0
    assert len(FakeRunner.export_calls) == 1
    assert FakeRunner.export_calls[0].export.run_id == "run-123"
