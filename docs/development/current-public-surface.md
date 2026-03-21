# Current Public Surface

This document captures the current user-facing surface before modernization work starts. It is the baseline for compatibility checks and migration notes.

## Public Packages and Imports

### `LinkedInWebScraper`
- `LinkedInJobScraper`
- `JobScraper`
- `JobScraperConfig`
- `JobScraperConfigFactory`
- `JobScraperAdvancedConfig`
- `JobDescriptionProcessor`
- `JobDataCleaner`
- `JobTitleClassifier`
- `OpenAIHandler`
- `FileManager`
- `Logger`
- `get_random_header`
- `fetch_until_success`
- constants re-exported from `Utils.constants`

### `Utils`
- `Logger`
- `FileManager`
- constants from `Utils.constants`

### `OpenAIHandler`
- `OpenAIHandler`

## Entry Points and Scripts
- `example.py`
  - imports from `LinkedInWebScraper`
  - creates a `Logger`
  - builds `JobScraperConfig`
  - instantiates `LinkedInJobScraper`
  - runs `.run()`
  - prints the resulting dataframe head
- `example_advanced_config.py`
  - same as `example.py` plus `JobScraperAdvancedConfig`
- `process_ds_jobs.py`
  - exposes `run_ds_daily_scraper(...)`
  - orchestrates multiple scraper runs by remote mode
  - saves CSV output through `FileManager`
- `main.py`
  - creates a `Logger`
  - runs `DailyScrapeService.run_daily()` for multiple cities
  - keeps compatibility-friendly bare filenames at the call site
  - resolves managed artifact paths internally

## Current Runtime Side Effects
- log files resolve under `artifacts/logs` by default when a bare filename is used:
  - `main.log`
  - `example.log`
  - `example_advanced_config.log`
- CSV files resolve under `artifacts/jobs` by default when a bare filename is used:
  - per-city or per-run exports
  - combined daily export from `main.py`
- explicit absolute paths or explicit nested relative paths still bypass the managed artifact directories
- OpenAI integration expects `OPENAI_API_KEY` in environment or `.env`
- importing modules can trigger broad cross-package imports because the current package layout re-exports many symbols at package import time

## Known Baseline Risks
- Packaging is `setup.py`-based only.
- There is no reproducible dev bootstrap in the repo yet.
- `OpenAIHandler` can participate in circular import paths.
- The current OpenAI integration uses `chat.completions`.
- The existing test suite includes a live OpenAI test, which is not suitable for default CI.
