# Validation

This page captures the long-term validation gates for risky changes in this repository.

## Default Validation

Run these checks after changes that can affect imports, runtime behavior, packaging, logging, persistence, or entrypoints:

- `python -m pytest -q`
- `python -m ruff check .`
- `python -m mkdocs build --strict`
- the current Pyrefly seam from `codex/config.toml`
- smoke tests for `example.py` and `main.py`

## Smoke Expectations

The baseline compatibility smoke checks are:

- `example.py` still orchestrates a scrape successfully with mocked dependencies
- `main.py` still orchestrates the daily run successfully with mocked dependencies
- generated outputs only appear in expected managed locations unless an explicit path is passed

## When Packaging Changes

- build the sdist and wheel
- verify the build succeeds from the current working tree
- verify canonical and legacy imports still load from an installed artifact when possible

## When Logging Changes

- verify the library does not configure global logging at import time
- verify script and CLI entrypoints still emit useful logs
- verify bare filenames resolve under `artifacts/logs/`

## When OpenAI Changes

- run offline adapter or handler tests
- only run live OpenAI tests when credentials are present and the test is explicitly selected
- verify the non-OpenAI scraper path still works without optional enrichment

## When Storage Changes

- run migration tests
- verify persistence works with the configured SQLite path
- verify export artifacts are still generated from persisted state

## Commit Rule

Risky changes end with green validation and one commit before the next risky checkpoint begins.
