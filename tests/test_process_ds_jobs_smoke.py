from __future__ import annotations

import importlib
import runpy
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class FakeLogger:
    filename: str

    def __post_init__(self) -> None:
        self.log = SimpleNamespace(info=MagicMock())


def test_process_ds_jobs_delegates_to_daily_service(monkeypatch):
    import process_ds_jobs

    calls = []
    expected = pd.DataFrame([{"Title": "Data Scientist"}])

    class FakeService:
        def __init__(self, logger, **kwargs):
            calls.append(("init", logger.filename, kwargs))

        def run_for_location(self, **kwargs):
            calls.append(("run_for_location", kwargs))
            return expected

    monkeypatch.setattr(process_ds_jobs, "DailyScrapeService", FakeService)

    result = process_ds_jobs.run_ds_daily_scraper(
        logger=FakeLogger("main.log"),
        location="Guadalajara",
        file_name="out.csv",
        output_dir="artifacts",
    )

    assert result is expected
    assert calls[0][0] == "init"
    assert calls[1][0] == "run_for_location"
    assert calls[1][1]["location"] == "Guadalajara"
    assert calls[1][1]["file_name"] == "out.csv"
    assert calls[1][1]["output_dir"] == "artifacts"


def test_process_ds_jobs_script_defaults_to_once_cli(monkeypatch):
    cli_main_module = importlib.import_module("linkedin_web_scraper.interfaces.cli.main")

    calls = []

    def fake_main(argv=None):
        calls.append(argv)
        return 0

    monkeypatch.setattr(cli_main_module, "main", fake_main)
    monkeypatch.setattr(sys, "argv", [str(ROOT / "process_ds_jobs.py")])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(ROOT / "process_ds_jobs.py"), run_name="__main__")

    assert exc_info.value.code == 0
    assert calls == [["scrape", "once"]]
