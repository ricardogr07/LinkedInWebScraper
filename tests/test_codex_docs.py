from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "codex" / "config.toml"
TOOLS_DOC = ROOT / "docs" / "codex" / "tools-and-commands.md"
INTEGRATIONS_DOC = ROOT / "docs" / "codex" / "integrations.md"


def test_codex_config_parses_and_has_expected_sections():
    data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    assert set(data) >= {"project", "rules", "commands", "integrations", "subagents", "skills"}
    assert data["project"]["name"] == "LinkedInWebScraper"
    assert data["rules"]["commit_after_risky_change"] is True


def test_codex_commands_are_documented():
    data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    tools_doc = TOOLS_DOC.read_text(encoding="utf-8")

    for name, command_data in data["commands"].items():
        assert f"`{name}`" in tools_doc
        assert command_data["command"] in tools_doc


def test_codex_integrations_are_documented():
    data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    integrations_doc = INTEGRATIONS_DOC.read_text(encoding="utf-8")

    for name in data["integrations"]:
        assert f"`{name}`" in integrations_doc
