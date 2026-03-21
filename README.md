# LinkedInWebScraper

LinkedInWebScraper is a production-minded Python library and scheduled job runner for collecting LinkedIn job listings, normalizing the data, persisting run history, and exporting reusable datasets.

## Highlights

- Canonical package namespace under `linkedin_web_scraper`
- Typed programmatic config for single scrapes and TOML runtime config for CLI/scheduled runs
- Managed artifacts under `artifacts/jobs`, `artifacts/logs`, and `artifacts/state`
- SQLite-backed persistence through a clean application storage port
- Package CLI with `scrape once`, `scrape daily`, `export`, and `--dry-run`
- Optional OpenAI enrichment built on the current Responses API
- Backward-compatible wrappers for `LinkedInWebScraper`, `Utils`, `OpenAIHandler`, `main.py`, and `process_ds_jobs.py`

## Architecture

The canonical package is organized into explicit layers:

- `config`: typed library and runtime configuration models
- `application`: orchestration services such as `LinkedInJobScraper`, `DailyScrapeService`, and `RuntimeRunner`
- `domain`: dataframe cleaning and title-classification logic
- `infra`: HTTP, logging, paths, OpenAI, SQLite, and CSV helpers
- `interfaces`: CLI entrypoints and runtime surfaces

## Installation

Base install:

```bash
pip install LinkedInWebScraper
```

Install with optional OpenAI enrichment support:

```bash
pip install LinkedInWebScraper[openai]
```

For local development:

```bash
pip install -e .[dev]
```

## Quickstart

Programmatic single scrape:

```python
from linkedin_web_scraper import (
    JobScraperConfig,
    LinkedInJobScraper,
    RemoteType,
    configure_logging,
)

logger = configure_logging(filename="example.log")
config = JobScraperConfig(
    position="Data Analyst",
    location="San Francisco",
    remote=RemoteType.REMOTE,
)

jobs = LinkedInJobScraper(logger=logger, config=config).run()
print(jobs.head())
```

## CLI Runtime

The package CLI now supports runtime-configured execution:

```bash
linkedin-webscraper scrape once --dry-run
linkedin-webscraper scrape daily
linkedin-webscraper export --run-id <run-id>
```

Use `runtime.example.toml` as the template for a real `runtime.toml`. The CLI also honors lightweight env overrides such as:

- `LINKEDIN_WEB_SCRAPER_CONFIG`
- `LINKEDIN_WEB_SCRAPER_STORAGE_URL`
- `LINKEDIN_WEB_SCRAPER_OUTPUT_DIR`
- `LINKEDIN_WEB_SCRAPER_LOG_LEVEL`
- `LINKEDIN_WEB_SCRAPER_OPENAI_ENABLED`
- `LINKEDIN_WEB_SCRAPER_OPENAI_MODEL`

The compatibility wrapper `python main.py` still defaults to `scrape daily`, and `python process_ds_jobs.py` defaults to `scrape once`.

## Storage Model

SQLite persistence is enabled by default for CLI and daily-service runs:

- `scrape_runs` tracks run lifecycle metadata
- `jobs` stores the latest canonical attributes per `JobID`
- `job_snapshots` stores the per-run dataframe payload
- `job_enrichments` stores OpenAI audit data when enrichment is present
- CSV files are downstream artifacts exported from persisted run data

The managed default database path is `artifacts/state/linkedin_jobs.sqlite`.

## OpenAI Enrichment

OpenAI-backed enrichment is optional.

- Install `LinkedInWebScraper[openai]`
- Set `OPENAI_API_KEY` in the environment
- Enable it programmatically with `JobScraperConfig(openai_enabled=True, openai_model="gpt-4o-mini")`
- Or enable it at runtime with TOML / env-driven CLI settings
- Enrichment failures fall back to the base cleaned dataset instead of aborting the scrape

For a PowerShell session on Windows:

```powershell
$env:OPENAI_API_KEY = "sk-..."
python example_openai.py
```

To persist the key for your Windows user account without storing it in the repo:

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

## Runtime Config Template

The tracked runtime template is [runtime.example.toml](runtime.example.toml). It covers:

- logging file and level
- SQLite state path or DSN overrides
- single-location scrape defaults
- daily multi-city scrape defaults
- persisted-run export defaults

Keep secrets out of TOML. `OPENAI_API_KEY` stays env-only.

## Docker

A slim container runtime is included through [Dockerfile](Dockerfile).

Build the base image:

```bash
docker build -t linkedin-webscraper .
```

Build with the optional OpenAI extra installed:

```bash
docker build --build-arg INSTALL_EXTRAS=openai -t linkedin-webscraper:openai .
```

Run a daily scrape with mounted artifacts and a mounted runtime config:

```bash
docker run --rm \
  -v ${PWD}/artifacts:/app/artifacts \
  -v ${PWD}/runtime.toml:/app/runtime.toml \
  -e LINKEDIN_WEB_SCRAPER_CONFIG=/app/runtime.toml \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  linkedin-webscraper:openai scrape daily
```

## CI/CD And Automation

The repository now includes four operational workflows under `.github/workflows/`:

- `ci.yml` runs the tox matrix on pushes and pull requests
- `docs.yml` builds and deploys MkDocs to GitHub Pages from `main`
- `release.yml` builds distributions and publishes them through trusted publishing to TestPyPI and PyPI
- `daily-scrape.yml` runs the scheduled daily scrape, stores SQLite state on the `data` branch, uploads artifacts, and raises an issue on automation failures

The scheduled workflow uses `.github/runtime/daily.toml` and currently runs at `12:30 UTC` every day.

## Compatibility Notes

- New code should import from `linkedin_web_scraper`
- Legacy namespaces such as `LinkedInWebScraper`, `Utils`, and `OpenAIHandler` still work through shims
- `example.py`, `example_openai.py`, `main.py`, and `process_ds_jobs.py` remain compatibility-sensitive smoke paths

## Development

Default local checks:

```bash
python -m pytest -q
python -m ruff check .
python -m mkdocs build --strict
python -m pyrefly check src/linkedin_web_scraper/config/job_scraper_config.py src/linkedin_web_scraper/config/job_scraper_advanced_config.py src/linkedin_web_scraper/config/job_scraper_config_factory.py src/linkedin_web_scraper/config/openai.py src/linkedin_web_scraper/config/storage.py src/linkedin_web_scraper/config/options.py src/linkedin_web_scraper/config/runtime.py src/linkedin_web_scraper/application/daily_scrape_service.py src/linkedin_web_scraper/application/linkedin_job_scraper.py src/linkedin_web_scraper/application/storage.py src/linkedin_web_scraper/application/runtime_runner.py src/linkedin_web_scraper/domain/job_data_cleaner.py src/linkedin_web_scraper/domain/job_title_classifier.py src/linkedin_web_scraper/infra/logging.py src/linkedin_web_scraper/infra/paths.py src/linkedin_web_scraper/infra/http/policy.py src/linkedin_web_scraper/infra/http/utils.py src/linkedin_web_scraper/infra/http/job_scraper.py src/linkedin_web_scraper/infra/openai/models.py src/linkedin_web_scraper/infra/openai/openai_handler.py src/linkedin_web_scraper/infra/openai/job_description_processor.py src/linkedin_web_scraper/infra/storage/models.py src/linkedin_web_scraper/infra/storage/sqlite.py
```

## License

This project is licensed under the MIT License.