# Getting Started

## Installation

Install the published package:

```bash
pip install LinkedInWebScraper
```

Install the optional OpenAI enrichment extra when you need description post-processing:

```bash
pip install LinkedInWebScraper[openai]
```

For local development:

```bash
pip install -e .[dev]
```

## Scrape One Search

Use the canonical package imports for new code:

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

Bare log names resolve to `artifacts/logs/`. Bare CSV output names resolve to `artifacts/jobs/`.

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

Set `OPENAI_API_KEY` in the environment before running the scraper. The library does not load `.env` files during import. If enrichment setup fails, the scraper returns the base cleaned dataset instead of aborting the full run.

## Run The Example Scripts

These compatibility-oriented scripts remain useful during the modernization:

```bash
python example.py
python example_advanced_config.py
```

## Run The Daily Workflow

The current scheduled-job entrypoint is still `main.py`:

```bash
python main.py
```

That workflow uses `DailyScrapeService` under the hood and writes city-level plus combined CSV outputs to `artifacts/jobs/` by default.

## Migration Guidance

- Prefer imports from `linkedin_web_scraper` in new code.
- Keep existing legacy imports only when you are explicitly validating backward compatibility.
- Treat `example.py` and `main.py` as compatibility-sensitive smoke paths during refactors.

## Validate Local Changes

The default local quality gates are:

```bash
python -m pytest -q
python -m ruff check .
python -m mkdocs build --strict
```

For the currently enforced type-check seam, run:

```bash
python -m pyrefly check src/linkedin_web_scraper/config/job_scraper_config.py src/linkedin_web_scraper/config/job_scraper_advanced_config.py src/linkedin_web_scraper/config/job_scraper_config_factory.py src/linkedin_web_scraper/config/openai.py src/linkedin_web_scraper/config/options.py src/linkedin_web_scraper/application/daily_scrape_service.py src/linkedin_web_scraper/application/linkedin_job_scraper.py src/linkedin_web_scraper/domain/job_data_cleaner.py src/linkedin_web_scraper/domain/job_title_classifier.py src/linkedin_web_scraper/infra/logging.py src/linkedin_web_scraper/infra/paths.py src/linkedin_web_scraper/infra/http/policy.py src/linkedin_web_scraper/infra/http/utils.py src/linkedin_web_scraper/infra/http/job_scraper.py src/linkedin_web_scraper/infra/openai/models.py src/linkedin_web_scraper/infra/openai/openai_handler.py src/linkedin_web_scraper/infra/openai/job_description_processor.py
```
