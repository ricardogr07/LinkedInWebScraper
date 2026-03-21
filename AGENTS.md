# Agent Guide

Use these files first:
- `docs/development/validation.md`
- `docs/development/release-and-automation.md`
- `docs/codex/`
- `examples/`

Core repo rules:
- Treat risky changes as gated work: keep tests green, keep the `examples/`, `main.py`, and `process_ds_jobs.py` smoke paths working, and commit after each risky increment.
- Main agent owns final integration, validation, and commits.
- Subagents must have explicit, non-overlapping write scopes and must not revert each other's work.
- Prefer documented repo commands from `codex/config.toml` and `docs/codex/tools-and-commands.md`.
- `codex/config.toml` is a template/catalog only. Do not store secrets, local tokens, or machine-specific credentials in it.

This file is intentionally short. Detailed guidance lives in `docs/codex/`.
