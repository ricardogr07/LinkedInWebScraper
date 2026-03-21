from __future__ import annotations

import importlib
import runpy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_main_daily_run_smoke(monkeypatch):
    cli_main_module = importlib.import_module("linkedin_web_scraper.interfaces.cli.main")

    calls = []

    def fake_main(argv=None):
        calls.append(argv)
        return 0

    monkeypatch.setattr(cli_main_module, "main", fake_main)
    monkeypatch.setattr(sys, "argv", [str(ROOT / "main.py")])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(ROOT / "main.py"), run_name="__main__")

    assert exc_info.value.code == 0
    assert calls == [["scrape", "daily"]]
