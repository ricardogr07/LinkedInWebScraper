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
class FakeConfig:
    position: str
    location: str
    remote: str
    enrichment_provider: str
    enrichment_model: str


class FakeScraper:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def run(self):
        return pd.DataFrame(
            [
                {
                    "Title": "Data Scientist",
                    "Company": "Acme Corp",
                    "EnrichmentProvider": self.config.enrichment_provider,
                }
            ]
        )


def test_example_openai_script_smoke(monkeypatch):
    import linkedin_web_scraper

    captured = []

    monkeypatch.setattr(linkedin_web_scraper, "Logger", FakeLogger)
    monkeypatch.setattr(linkedin_web_scraper, "JobScraperConfig", FakeConfig)
    monkeypatch.setattr(linkedin_web_scraper, "LinkedInJobScraper", FakeScraper)
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: captured.append(args))

    runpy.run_path(str(ROOT / "examples" / "example_openai.py"), run_name="__main__")

    assert captured
    assert captured[-1][0].to_string(index=False).find("OPENAI") != -1
