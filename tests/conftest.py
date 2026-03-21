from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (ROOT, SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "live_linkedin: marks tests that require live LinkedIn access"
    )
    config.addinivalue_line("markers", "live_openai: marks tests that require live OpenAI access")
