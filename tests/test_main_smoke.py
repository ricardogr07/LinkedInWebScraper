from __future__ import annotations

import runpy
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class FakeLogger:
    filename: str

    def __post_init__(self) -> None:
        self.log = SimpleNamespace(info=MagicMock())


def test_main_daily_run_smoke(monkeypatch):
    import process_ds_jobs
    import Utils.logger

    scraped_calls = []

    def fake_run_ds_daily_scraper(*, logger, location, file_name, **kwargs):
        scraped_calls.append((logger.filename, location, file_name, kwargs))
        return None

    csv_frames = {
        "LinkedIn_Jobs_Data_Scientist_Monterrey.csv": pd.DataFrame([{"Title": "MTY"}]),
        "LinkedIn_Jobs_Data_Scientist_Guadalajara.csv": pd.DataFrame([{"Title": "GDL"}]),
        "LinkedIn_Jobs_Data_Scientist_Mexico_City.csv": pd.DataFrame([{"Title": "CDMX"}]),
    }

    read_csv_calls = []

    def fake_read_csv(path, *args, **kwargs):
        read_csv_calls.append(path)
        return csv_frames[path]

    to_csv_mock = MagicMock()

    monkeypatch.setattr(process_ds_jobs, "run_ds_daily_scraper", fake_run_ds_daily_scraper)
    monkeypatch.setattr(Utils.logger, "Logger", FakeLogger)
    monkeypatch.setattr(pd, "read_csv", fake_read_csv)
    monkeypatch.setattr(pd.DataFrame, "to_csv", to_csv_mock)

    runpy.run_path(str(ROOT / "main.py"), run_name="__main__")

    assert [call[1] for call in scraped_calls] == ["Monterrey", "Guadalajara", "Mexico City"]
    assert read_csv_calls == [
        "LinkedIn_Jobs_Data_Scientist_Monterrey.csv",
        "LinkedIn_Jobs_Data_Scientist_Guadalajara.csv",
        "LinkedIn_Jobs_Data_Scientist_Mexico_City.csv",
    ]
    assert to_csv_mock.call_args.args[0] == "LinkedIn_Jobs_Data_Scientist_Mexico.csv"
