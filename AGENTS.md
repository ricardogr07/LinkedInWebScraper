# Agent Guide

Use these files first:
- `PLAN.md`
- `docs/development/validation.md`
- `docs/codex/`

Core repo rules:
- Treat risky changes as gated work: keep tests green, keep the `example.py` and `main.py` smoke paths working, and commit after each risky increment.
- Main agent owns final integration, validation, and commits.
- Subagents must have explicit, non-overlapping write scopes and must not revert each other's work.
- Prefer documented repo commands from `codex/config.toml` and `docs/codex/tools-and-commands.md`.
- `codex/config.toml` is a template/catalog only. Do not store secrets, local tokens, or machine-specific credentials in it.

This file is intentionally short. Detailed guidance lives in `docs/codex/`.
