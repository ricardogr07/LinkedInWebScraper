from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd


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
