# Validation

This page captures the long-term validation gates for risky changes in this repository.

## Default Validation

Run these checks after changes that can affect imports, runtime behavior, packaging, logging, persistence, entrypoints, or deployment automation:

- `python -m pytest -q`
- `python -m ruff check .`
- `python -m mkdocs build --strict`
- the current Pyrefly seam from `codex/config.toml`
- smoke checks for `example.py`, `main.py`, and `process_ds_jobs.py`

## Smoke Expectations

The baseline compatibility smoke checks are:

- `example.py` still orchestrates a scrape successfully with mocked dependencies
- `main.py` still defaults to the canonical daily CLI path
- `process_ds_jobs.py` still defaults to the canonical once CLI path
- managed outputs only appear in expected artifact/state locations unless an explicit path is passed

## When Runtime Or CLI Changes

- run the CLI/runtime config tests first
- verify `--dry-run` still resolves plans without network access
- verify `main.py` and `process_ds_jobs.py` still route through the canonical CLI surface
- verify TOML runtime loading and env overrides keep the documented precedence order

## When Packaging Changes

- build the sdist and wheel
- verify the build succeeds from the current working tree
- verify canonical and legacy imports still load from an installed artifact when possible
- verify optional features remain optional at import time when dependencies move behind extras

## When Logging Changes

- verify the library does not configure global logging at import time
- verify script and CLI entrypoints still emit useful logs
- verify bare filenames resolve under `artifacts/logs/`

## When OpenAI Changes

- run offline OpenAI handler and processor tests first
- only run live OpenAI tests when credentials are present and the test is explicitly selected
- verify the non-OpenAI scraper path still works without optional enrichment
- verify OpenAI setup failures fall back to the base cleaned dataset instead of aborting the run

## When Storage Changes

- run SQLite storage adapter tests and daily-service persistence/export tests
- verify persistence works with the configured SQLite path
- verify export artifacts are still generated from persisted state
- verify managed database paths resolve under `artifacts/state/` by default

## When Container Or Deployment Assets Change

- validate the runtime config template, `.github/runtime/daily.toml`, and deployment docs together
- keep container validation indirect in the default offline suite
- verify mounted `artifacts/` and runtime config paths match the documented contract
- verify workflow files still cover CI, docs publish, release publishing, and the daily scheduled scrape

## Commit Rule

Risky changes end with green validation and one commit before the next risky checkpoint begins.