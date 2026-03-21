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
  - runs `run_ds_daily_scraper(...)` for multiple cities
  - reads CSV files from repo root
  - concatenates them into `LinkedIn_Jobs_Data_Scientist_Mexico.csv`

## Current Runtime Side Effects
- log files can be created in the repo root:
  - `main.log`
  - `example.log`
  - `example_advanced_config.log`
  - `openai.log`
  - `fetch_jobs.log`
- CSV files can be created in the repo root:
  - per-city or per-run exports
  - combined daily export from `main.py`
- OpenAI integration expects `OPENAI_API_KEY` in environment or `.env`
- importing modules can trigger broad cross-package imports because the current package layout re-exports many symbols at package import time

## Known Baseline Risks
- Packaging is `setup.py`-based only.
- There is no reproducible dev bootstrap in the repo yet.
- `OpenAIHandler` can participate in circular import paths.
- The current OpenAI integration uses `chat.completions`.
- The existing test suite includes a live OpenAI test, which is not suitable for default CI.
