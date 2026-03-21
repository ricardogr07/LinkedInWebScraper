# Codex Enablement

This section is an internal developer support pack for using Codex effectively in this repository. It exists to make later refactors safer, more repeatable, and easier to delegate.

## What This Covers
- repo-specific agent rules and validation gates
- subagent usage patterns
- observed built-in skills and a future custom skill blueprint
- exact local commands for test, lint, docs, builds, and smoke checks
- recommended integrations for OpenAI docs and GitHub workflows

## Source of Truth
- Architecture and migration sequencing: `PLAN.md`
- Risky-change validation rules: `COMPATIBILITY_CHECKLIST.md`
- Agent workflow and Codex-specific guidance: this `docs/codex/` section
- Template command/integration catalog: `codex/config.toml`

## Status Model
- `available_now`: usable in the current environment without extra setup
- `recommended_later`: worth standardizing, but not assumed to be installed in-session
- `blocked_or_misconfigured`: present or intended, but not currently usable from this environment

## Current Environment Snapshot

### Available Now
- `python` is installed and is the project runtime
- `git` is installed
- the repo-local Python toolchain works through `python -m ...`
- `codex.exe` exists through the VS Code extension install

### Recommended Later
- `openai_docs` MCP is the primary recommended documentation integration for OpenAI work
- `github_mcp` is worth adding later for richer GitHub context once auth/setup is stable
- a future repo-specific skill can help with phased modernization work

### Blocked Or Misconfigured
- `gh` is installed, but the current GitHub auth token is invalid
- `docker` is installed, but the daemon/config are not currently usable from this session
- no MCP servers are visible in this session right now

## Why This Exists Before Phase 2
Phase 2 will introduce the canonical package layout and compatibility shims. That work benefits from explicit subagent roles, exact validation commands, and a shared record of which integrations are real versus merely aspirational.
