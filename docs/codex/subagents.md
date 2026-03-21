# Subagents

Use subagents to parallelize well-scoped work, not to outsource integration decisions.

## Default Rules
- Main agent owns the critical path, final validation, and commits.
- Every subagent must have an explicit write scope before it starts.
- Subagents must not revert changes from other agents.
- Prefer delegation for sidecar work that can run in parallel without blocking the next local step.
- Keep the final merge point local when the work is tightly coupled or likely to trigger follow-up edits.

## Explorer vs Worker
- `explorer`: ask specific codebase questions or gather facts fast. Use when the main task is blocked on repo understanding, not implementation.
- `worker`: use for bounded implementation or test/doc tasks with a clear file boundary.

## When To Delegate
- Add or tighten regression tests while the main agent works on implementation.
- Draft documentation while the main agent validates tooling.
- Build packaging, release, or storage artifacts in a disjoint area of the repo.
- Review a narrow subsystem before a larger refactor.

## When Not To Delegate
- The very next step depends on the result.
- The change is small enough to do locally faster than describing it.
- The task would require overlapping writes across the same files.
- The task is mostly integration judgment rather than bounded execution.

## Repo Role Catalog

### `tests_safety`
- Purpose: own smoke tests, regression fixtures, and validation harness updates.
- Write scope: `tests/`, plus small documentation updates under `docs/development/` when they are directly tied to validation rules.
- Use when: a risky refactor needs guardrails or failing behavior must be captured before implementation.

### `docs_devx`
- Purpose: own internal documentation, developer workflow notes, and Codex enablement material.
- Write scope: `docs/`, `mkdocs.yml`, and `codex/`.
- Use when: improving docs, local developer setup, command references, or workflow guidance.

### `packaging_release`
- Purpose: own build metadata, packaging config, wheel validation, and release-oriented documentation.
- Write scope: `pyproject.toml`, `tox.toml`, `setup.py`, and release docs.
- Use when: changing dependency management, package metadata, build commands, or publication flow.

### `storage_migrations`
- Purpose: own persistence adapters, schema migrations, and export/state contracts.
- Write scope: storage modules, migration files, and storage docs.
- Use when: adding SQLite, future PostgreSQL support, or state export behavior.

## Integration Responsibility
- Main agent validates the final state with the repo command set from `codex/config.toml`.
- Main agent decides commit boundaries.
- Subagents should return changed files, assumptions, and validation run, not a broad recap.
