from __future__ import annotations

import builtins
import runpy
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class FakeLogger:
    filename: str

    def __post_init__(self) -> None:
        self.log = SimpleNamespace(info=lambda *args, **kwargs: None)


@dataclass
class FakeAdvancedConfig:
    KEYWORDS: list[str]


@dataclass
class FakeConfig:
    position: str
    location: str
    remote: str
    advanced_config: FakeAdvancedConfig


class FakeScraper:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def run(self):
        return pd.DataFrame([{"Title": "Data Scientist", "Company": "Acme Corp"}])


def test_example_advanced_config_script_smoke(monkeypatch):
    import LinkedInWebScraper

    captured = []

    monkeypatch.setattr(LinkedInWebScraper, "Logger", FakeLogger)
    monkeypatch.setattr(LinkedInWebScraper, "JobScraperAdvancedConfig", FakeAdvancedConfig)
    monkeypatch.setattr(LinkedInWebScraper, "JobScraperConfig", FakeConfig)
    monkeypatch.setattr(LinkedInWebScraper, "LinkedInJobScraper", FakeScraper)
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: captured.append(args))

    runpy.run_path(str(ROOT / "examples" / "example_advanced_config.py"), run_name="__main__")

    assert captured
    assert captured[-1][0].to_string(index=False).find("Data Scientist") != -1
