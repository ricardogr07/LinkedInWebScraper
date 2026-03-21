# Compatibility Checklist

Run this checklist after every risky change involving imports, packaging, logging, persistence, entrypoints, or orchestration.

## Default Validation
- Run the offline test suite.
- Run packaging or import smoke checks from the current working tree.
- Run the script smoke checks for `example.py` and `main.py`.
- Review warnings or deprecations introduced by compatibility shims.

## If Packaging Changed
- Build an sdist and wheel.
- Install the wheel into a clean environment.
- Verify imports still work for:
  - `LinkedInWebScraper`
  - `Utils`
  - `OpenAIHandler`
  - future canonical package imports

## If Logging Changed
- Verify the library does not force global logging configuration at import time.
- Verify script entrypoints still emit useful logs.
- Verify tests do not create unexpected root-level log files.

## If OpenAI Integration Changed
- Run offline adapter tests.
- Only run live OpenAI tests when credentials are present and the test is explicitly selected.
- Verify the non-OpenAI scraper path still works without the extra installed.

## If Storage Changed
- Run migration tests.
- Verify persistence works with the configured SQLite path.
- Verify CSV export still works as a downstream artifact.

## Minimum Smoke Expectations
- `example.py` still orchestrates a scrape successfully with mocked dependencies.
- `main.py` still orchestrates the daily run successfully with mocked dependencies.
- Generated outputs are written only to expected locations for the current phase.
