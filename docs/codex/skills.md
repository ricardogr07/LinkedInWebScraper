# Skills

This page documents the Codex skills currently observed in this environment and a future skill blueprint for this repository.

## Current Built-In Skills

### `openai-docs`
- Purpose: use official OpenAI documentation as the primary source for OpenAI-related work.
- Use when: checking SDK compatibility, current API guidance, model selection, or OpenAI migration paths.
- Why it matters here: this repo still has OpenAI integration work ahead, so primary-source guidance is important.

### `skill-creator`
- Purpose: design or update reusable Codex skills.
- Use when: the repo reaches repeated workflows that deserve a dedicated skill.
- Why it matters here: later phases may justify a repo-specific modernization skill.

### `skill-installer`
- Purpose: install supported Codex skills into the local environment.
- Use when: a documented skill should become locally available without hand-copying files.

### `neon-pairwise-review`
- Purpose: run a governed pairwise review workflow over two candidate responses.
- Use when: the task is explicitly a pairwise review problem and the repo workflow fits that skill.

## Future Skill Blueprint

### `linkedin-modernization-maintainer`
- Status: planned only, not implemented in this subtask.
- Purpose: guide phased modernization in this repo with compatibility awareness and strict validation sequencing.

## Proposed Responsibilities
- map requests to the current modernization phase
- remind the agent about risky-change validation gates
- recommend safe subagent partitioning for tests, docs, packaging, or compatibility layers
- preserve the `examples/` scripts and `main.py`/`process_ds_jobs.py` behavior while deeper refactors land
- keep compatibility shims explicit during namespace migration

## Likely Inputs
- current phase goal
- target files or subsystem
- expected validation commands
- whether the change is compatibility-sensitive

## Likely Outputs
- a narrowed implementation checklist
- validation sequence
- recommended subagent roles and write scopes
- compatibility and rollback notes

The future skill should remain a workflow guide, not a replacement for the repo docs under `docs/development/` and `AGENTS.md`.