from __future__ import annotations

import runpy
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class FakeLogger:
    filename: str

    def __post_init__(self) -> None:
        self.log = SimpleNamespace(info=MagicMock())


def test_main_daily_run_smoke(monkeypatch):
    import Utils.logger
    from linkedin_web_scraper.application import daily_scrape_service

    calls = []

    class FakeService:
        def __init__(self, logger, **kwargs):
            calls.append(("init", logger.filename, kwargs))
            self.logger = logger

        def run_daily(self, **kwargs):
            calls.append(("run_daily", kwargs))
            return None

    monkeypatch.setattr(Utils.logger, "Logger", FakeLogger)
    monkeypatch.setattr(daily_scrape_service, "DailyScrapeService", FakeService)

    runpy.run_path(str(ROOT / "main.py"), run_name="__main__")

    assert calls[0][0] == "init"
    assert calls[0][1] == "main.log"
    assert calls[1] == ("run_daily", {})
