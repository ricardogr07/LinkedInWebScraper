# LinkedInWebScraper Modernization Plan

## Purpose
- Build a clean, reliable library and scheduled job runner for collecting LinkedIn job data, normalizing it, optionally enriching it with OpenAI, and persisting/exporting it in a repeatable way.
- Use this repo as both a production-grade library and a learning vehicle for clean architecture, testing discipline, packaging, CI/CD, and safe refactoring.
- Keep the current user-facing workflow working during the migration, especially `example.py` and `main.py`, with explicit compatibility checks after every risky change.

## Architectural Principles
- Keep a single canonical package namespace and isolate legacy imports behind compatibility shims.
- Separate pure domain logic from infrastructure concerns: HTTP, logging, OpenAI, filesystem, database, and scheduler.
- Avoid side effects at import time.
- Keep the library configurable via TOML plus environment overrides.
- Make optional features truly optional: OpenAI is an extra, live tests are opt-in, DB backend is behind an interface.
- Prefer standard-library primitives where possible: `logging`, `tomllib`, `pathlib`, typed dataclasses/enums.

## Working Rules
1. Any change that can break imports, runtime behavior, packaging, logging, persistence, or entrypoints must end with automated tests green, smoke checks for `example.py` and `main.py`, and one git commit before the next risky change.
2. Non-breaking tooling/documentation changes may be grouped, but only if the test suite stays green.
3. `example.py` and `main.py` must remain executable throughout the migration, either directly or through explicit compatibility wrappers.
4. Main agent owns integration, final review, and commits. Subagents only work on disjoint write scopes.

## Standard Validation After Every Risky Step
- Run the default offline suite.
- Run packaging/import smoke checks from an installed environment.
- Run smoke tests for `example.py` and `main.py`.
- If the step touches OpenAI, run offline adapter tests; live test only if credentials are present.
- If the step touches storage, run migration plus persistence regression tests.
- Commit only after the above pass.

## Suggested Breaking-Change Commit Boundaries
- Baseline smoke and regression harness
- TOML packaging/tooling foundation
- Canonical package plus legacy shims
- Logging replacement
- Config/application boundary refactor
- OpenAI adapter migration
- Storage interface plus SQLite adapter
- CLI/main runtime migration
- CI/release/scheduler rollout

## Phase 0: Baseline and Safety Net
### Why
- Before changing architecture, lock down what "still works" means and create fast checks that catch regressions early.

### Steps
1. Document the current public surface: imports, scripts, examples, outputs, and side effects.
2. Add smoke tests for `example.py` and `main.py` using mocks instead of live services.
3. Add fixture-based tests around current HTML parsing and cleaning behavior so refactors preserve output shape.
4. Define test markers for default offline tests plus optional `live_linkedin` and `live_openai`.
5. Add a lightweight compatibility checklist to run after every risky step.

### Parallelizable Work
- Worker A: smoke tests for `example.py` and `main.py`
- Worker B: scraper/parser fixtures and regression tests
- Worker C: compatibility checklist draft and dev workflow notes

### Commit Gates
- Commit after the smoke-test harness is in place and green.
- Commit after fixture coverage exists for current scraper behavior.

### Done When
- We can detect breakage in imports, orchestration, and scraper output without relying on live services.

## Phase 1: Packaging and Tooling Foundation
### Why
- The repo is not reproducible from a clean machine yet. Packaging and tooling must become deterministic before deeper refactors.

### Steps
1. Introduce `pyproject.toml` with PEP 621 metadata, `setuptools.build_meta`, runtime dependencies, optional extras, and a console script placeholder.
2. Add `tox.toml` for `py311`, `py312`, `py313`, `py314`, `lint`, `type`, `docs`, and `build`.
3. Add quality tools: `pytest`, coverage, `ruff`, and `pyrefly`.
4. Keep `setup.py` temporarily only as a compatibility bridge while validating `pyproject.toml`.
5. Prove installation from a built wheel, not just from source.
6. Remove or minimize legacy packaging files once wheel install/import checks pass.

### Parallelizable Work
- Worker A: `pyproject.toml`, extras, build settings
- Worker B: `tox.toml`, pytest, coverage, `ruff`, `pyrefly`
- Worker C: README developer setup updates

### Commit Gates
- Commit after `pyproject.toml` and `tox.toml` are introduced and the project builds.
- Commit after wheel install/import smoke checks pass and packaging is fully TOML-driven.

### Done When
- A new machine can install the project, run tests, build docs, and build a wheel through `tox`.

## Phase 2: Canonical Package Layout and Compatibility Layer
### Why
- Current imports are split across `LinkedInWebScraper`, `Utils`, and `OpenAIHandler`, and there is at least one circular-import path. This must be normalized before deeper cleanup.

### Steps
1. Introduce the canonical package: `src/linkedin_web_scraper`.
2. Define internal module boundaries: `config`, `domain`, `application`, `infra/http`, `infra/openai`, `infra/storage`, and `interfaces/cli`.
3. Move code gradually into the canonical package without removing old imports yet.
4. Add compatibility shims for `LinkedInWebScraper`, `Utils`, and `OpenAIHandler`.
5. Add deprecation warnings to legacy import paths.
6. Remove circular import paths by keeping cross-module imports one-directional.
7. Keep `example.py` and `main.py` pointing to stable wrappers until the new package is proven.

### Parallelizable Work
- Worker A: canonical package scaffolding
- Worker B: legacy import shims and deprecation wrappers
- Worker C: import/packaging regression tests

### Commit Gates
- Commit after the canonical package exists and legacy imports still work.
- Commit after circular imports are removed and smoke tests for examples/scripts are green.

### Done When
- The new namespace is real, the old namespace still works, and imports are no longer fragile.

## Phase 3: Core Architecture Cleanup
### Why
- The library needs cleaner boundaries, fewer side effects, and more explicit dependencies.

### Steps
1. Replace the singleton `Logger` with standard `logging`.
2. Convert config objects to typed dataclasses and enums.
3. Introduce a request client abstraction with `requests.Session`, retry/backoff policy, and explicit timeouts.
4. Separate orchestration from implementation so application services coordinate runs and lower-level modules stay focused.
5. Clean encoding issues and constants organization.
6. Move generated outputs out of repo root into configured artifact/state directories.

### Parallelizable Work
- Worker A: logging refactor
- Worker B: typed config/enums
- Worker C: HTTP client and retry policy extraction

### Commit Gates
- Commit after logging migration while keeping `example.py` and `main.py` working.
- Commit after config and orchestration boundaries are stabilized.

### Done When
- Core modules are testable in isolation and infra concerns are no longer baked into every class.

## Phase 4: Test Strategy, Types, and Documentation
### Why
- Production quality requires fast feedback, type safety, and documentation generated from the code.

### Steps
1. Expand unit tests for URL generation, parser behavior, cleaner transformations, classifier logic, logging configuration, and entrypoint orchestration.
2. Add integration tests using saved HTML fixtures and mocked HTTP.
3. Add `pyrefly` incrementally, starting on the canonical package only.
4. Standardize docstrings for all public classes and functions.
5. Add `mkdocs.yml` with MkDocs Material and `mkdocstrings`.
6. Rewrite the README around install, quickstart, configuration, optional OpenAI usage, storage, and migration notes.

### Parallelizable Work
- Worker A: test expansion
- Worker B: docstring pass
- Worker C: MkDocs and README restructure

### Commit Gates
- Commit after offline test coverage meaningfully improves.
- Commit after docs build cleanly from source docstrings.

### Done When
- Docs are generated from code, type checking is active, and the default suite is reliable and offline.

## Phase 5: OpenAI Enrichment Modernization
### Why
- The current integration uses older API patterns and should become optional, typed, auditable, and failure-tolerant.

### Steps
1. Define an enrichment interface separate from the scraper core.
2. Implement an OpenAI adapter using the current Responses API and structured outputs.
3. Make OpenAI an optional dependency extra.
4. Read API credentials from environment only; local `.env` loading belongs in CLI/dev tooling, not import paths.
5. Make model/config selection TOML- and env-driven.
6. Store enrichment metadata and raw parsed payloads for audit/debug.
7. Ensure enrichment failures degrade gracefully and never fail the base scrape.

### Parallelizable Work
- Worker A: enrichment interface and typed schema
- Worker B: OpenAI adapter and config wiring
- Worker C: offline tests plus optional live marker tests

### Commit Gates
- Commit after the adapter is introduced behind an interface.
- Commit after the old handler is replaced by compatibility wrappers and tests pass.

### Done When
- AI enrichment is optional, modern, typed, and isolated from scraper correctness.

## Phase 6: Storage Interface and Extensible SQL Persistence
### Why
- We need durable storage now for local work and GitHub Actions, without closing the door to Azure/GCP later.

### Steps
1. Define a storage port with methods to begin/end scrape runs, upsert jobs, record snapshots, store enrichment results, and export outputs.
2. Implement the first adapter with SQLAlchemy 2.0.
3. Use SQLite first with DSN-based configuration so local dev and GitHub Actions share the same contract.
4. Add Alembic migrations.
5. Model at least `scrape_runs`, `jobs`, `job_snapshots`, and `job_enrichments`.
6. Keep CSV export as a downstream output from the DB, not the source of truth.
7. Make backend extensibility explicit so later PostgreSQL on Azure/GCP can reuse the same application services.
8. Define the GitHub Actions persistence contract around a `data` branch holding the SQLite state.

### Parallelizable Work
- Worker A: storage interface and repositories
- Worker B: SQLAlchemy models and Alembic
- Worker C: export pipeline and state-branch workflow contract

### Commit Gates
- Commit after the storage interface exists and is wired behind the app service.
- Commit after SQLite persistence and migrations are working.
- Commit after CSV export comes from persisted state.

### Done When
- Local development, GitHub-hosted schedules, and future cloud DBs all fit the same abstraction.

## Phase 7: Runtime, CLI, Main Script, and Containerization
### Why
- The library should run cleanly as a library, a CLI, and a scheduled job.

### Steps
1. Add TOML runtime config using `tomllib`.
2. Introduce a CLI with commands such as `scrape once`, `scrape daily`, and `export`.
3. Refactor `main.py` into a thin compatibility wrapper over the new application service or CLI.
4. Keep `process_ds_jobs.py` as a compatibility entrypoint until replaced cleanly.
5. Add dry-run and test-friendly seams so scheduled orchestration can be validated without live scraping.
6. Add Docker support with mounted state/artifact directories and env-driven configuration.

### Parallelizable Work
- Worker A: TOML config loader and CLI
- Worker B: `main.py` and daily-run wrapper migration
- Worker C: Dockerfile and runtime docs

### Commit Gates
- Commit after CLI exists and `main.py` still works.
- Commit after container build and smoke checks pass.

### Done When
- We can run the scraper locally, by script, or in a container with the same core service.

## Phase 8: CI/CD, Docs Publish, PyPI, and Daily Automation
### Why
- Production quality is incomplete without automated verification, release hygiene, and scheduled operations.

### Steps
1. Add a CI workflow that runs `tox` on pushes and PRs.
2. Add docs build and publish workflow.
3. Add release workflow for TestPyPI/PyPI trusted publishing.
4. Add a scheduled GitHub Actions workflow for daily scraping using the `data` branch persistence model.
5. Add safeguards including concurrency control, artifact retention, notifications, and migrations before run.
6. Document release and rollback procedures.

### Parallelizable Work
- Worker A: CI matrix
- Worker B: docs/release workflows
- Worker C: scheduled scrape workflow and state-branch handling

### Commit Gates
- Commit after CI is enforcing tests and type/lint gates.
- Commit after release automation is proven in TestPyPI.
- Commit after scheduled daily run is validated end-to-end.

### Done When
- The project can test, publish, document, and run on a schedule automatically.

## Assumptions
- Python floor is `3.11+`.
- OpenAI remains optional and disabled by default.
- SQLite is the first persistence backend.
- GitHub-hosted scheduled runs persist the SQLite database through the `data` branch.
- Backward compatibility is preserved through wrappers and deprecation shims until a later major version removes them intentionally.
