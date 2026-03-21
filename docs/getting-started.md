# Getting Started

## Installation

Base install:

```bash
pip install LinkedInWebScraper
```

Install the optional OpenAI extra when you need enrichment:

```bash
pip install LinkedInWebScraper[openai]
```

For local development:

```bash
pip install -e .[dev]
```

## Programmatic Scrape

Use canonical imports for new code:

```python
from linkedin_web_scraper import (
    JobScraperConfig,
    LinkedInJobScraper,
    RemoteType,
    configure_logging,
)

logger = configure_logging(filename="example.log")
config = JobScraperConfig(
    position="Data Scientist",
    location="Monterrey",
    remote=RemoteType.REMOTE,
)

jobs = LinkedInJobScraper(logger=logger, config=config).run()
print(jobs.head())
```

## Enable OpenAI Enrichment

```python
config = JobScraperConfig(
    position="Data Scientist",
    location="Monterrey",
    remote=RemoteType.REMOTE,
    openai_enabled=True,
    openai_model="gpt-4o-mini",
)
```

Set `OPENAI_API_KEY` in the environment before running the scraper. The library does not load `.env` files during import.

For the current PowerShell session on Windows:

```powershell
$env:OPENAI_API_KEY = "sk-..."
python examples/example_openai.py
```

To persist the key for your user account on Windows without committing it:

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

## CLI Quickstart

Use the runtime template as a starting point:

```bash
copy runtime.example.toml runtime.toml
```

Preview a once scrape without hitting LinkedIn:

```bash
linkedin-webscraper scrape once --config runtime.toml --dry-run
```

Run the daily workflow:

```bash
linkedin-webscraper scrape daily --config runtime.toml
```

Export a persisted run from SQLite:

```bash
linkedin-webscraper export --config runtime.toml --run-id <run-id>
```

## Examples

The runnable examples live under `examples/`:

```bash
python examples/example.py
python examples/example_advanced_config.py
python examples/example_openai.py
```

## Compatibility Scripts

The modernization keeps the old root script surfaces working for compatibility:

```bash
python main.py
python process_ds_jobs.py
```

`main.py` defaults to the daily workflow. `process_ds_jobs.py` defaults to the single-location once workflow.

## Managed Artifacts

By default:

- logs go to `artifacts/logs`
- CSV exports go to `artifacts/jobs`
- SQLite state goes to `artifacts/state/linkedin_jobs.sqlite`

## Validate Local Changes

Default local checks:

```bash
python -m pytest -q
python -m ruff check .
python -m mkdocs build --strict
```

Current enforced Pyrefly seam:

```bash
python -m pyrefly check src/linkedin_web_scraper/config/job_scraper_config.py src/linkedin_web_scraper/config/job_scraper_advanced_config.py src/linkedin_web_scraper/config/job_scraper_config_factory.py src/linkedin_web_scraper/config/openai.py src/linkedin_web_scraper/config/storage.py src/linkedin_web_scraper/config/options.py src/linkedin_web_scraper/config/runtime.py src/linkedin_web_scraper/application/daily_scrape_service.py src/linkedin_web_scraper/application/linkedin_job_scraper.py src/linkedin_web_scraper/application/storage.py src/linkedin_web_scraper/application/runtime_runner.py src/linkedin_web_scraper/domain/job_data_cleaner.py src/linkedin_web_scraper/domain/job_title_classifier.py src/linkedin_web_scraper/infra/logging.py src/linkedin_web_scraper/infra/paths.py src/linkedin_web_scraper/infra/http/policy.py src/linkedin_web_scraper/infra/http/utils.py src/linkedin_web_scraper/infra/http/job_scraper.py src/linkedin_web_scraper/infra/openai/models.py src/linkedin_web_scraper/infra/openai/openai_handler.py src/linkedin_web_scraper/infra/openai/job_description_processor.py src/linkedin_web_scraper/infra/storage/models.py src/linkedin_web_scraper/infra/storage/sqlite.py
```