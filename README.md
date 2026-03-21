# LinkedInWebScraper

LinkedInWebScraper is a production-minded Python library and daily job runner for collecting LinkedIn job listings, normalizing the results, and exporting datasets that are easy to reuse in analysis pipelines.

## Highlights

- Canonical package namespace under `linkedin_web_scraper`
- Typed scraper configuration for locations, remote modes, time filters, and the optional OpenAI model
- Durable CSV export flow with managed artifact directories under `artifacts/`
- Daily multi-city orchestration through `main.py` or `DailyScrapeService`
- Optional OpenAI enrichment path built on the current Responses API
- Backward-compatible legacy imports while the migration stays in place

## Architecture

The canonical package is organized into a small set of explicit layers:

- `config`: typed configuration models, enums, and constants
- `application`: orchestration services such as `LinkedInJobScraper` and `DailyScrapeService`
- `domain`: dataframe cleaning and title-classification logic
- `infra`: HTTP, logging, path resolution, OpenAI, and storage helpers
- `interfaces`: CLI entrypoints and external runtime surfaces

## Installation

Base install:

```bash
pip install LinkedInWebScraper
```

Install with OpenAI enrichment support:

```bash
pip install LinkedInWebScraper[openai]
```

For local development:

```bash
pip install -e .[dev]
```

## Quickstart

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

scraper = LinkedInJobScraper(logger=logger, config=config)
job_data = scraper.run()
print(job_data.head())
```

The bare log name above resolves to `artifacts/logs/example.log`. Bare CSV export names resolve to `artifacts/jobs/`.

## Daily Run

Run the current daily workflow with:

```bash
python main.py
```

This writes per-city and combined CSV exports under `artifacts/jobs/` and logs under `artifacts/logs/` unless you pass explicit paths through the service layer. The compatibility examples in `example.py` and `example_advanced_config.py` remain valid.

## Storage Model

The current Phase 5 storage model is still file-based:

- job CSV exports are treated as managed artifacts under `artifacts/jobs/`
- log files are managed under `artifacts/logs/`
- no SQL database is part of the default runtime yet

Database-backed persistence is planned for a later phase, so the current library behavior remains simple, local, and easy to validate in offline tests.

## OpenAI Enrichment

OpenAI-backed enrichment is optional at runtime.

- Install the optional extra before enabling it: `pip install LinkedInWebScraper[openai]`
- Set `OPENAI_API_KEY` in the environment before running the scraper
- Use `JobScraperConfig(openai_enabled=True, openai_model="gpt-4o-mini")` to enable it
- Enrichment failures degrade gracefully and return the base scraped dataset instead of aborting the run
- Enriched rows include audit columns such as `OpenAIModel`, `OpenAIResponseId`, and `OpenAIRawPayload`

## Migration Notes

- New code should import from `linkedin_web_scraper`.
- Legacy namespaces such as `LinkedInWebScraper`, `Utils`, and `OpenAIHandler` still work through compatibility shims.
- `example.py` and `main.py` remain compatibility-sensitive smoke paths and are validated during risky refactors.

## Documentation

Project documentation is built with MkDocs. The main pages cover:

- library overview and runtime behavior
- programmatic configuration and artifact handling
- generated API reference from code docstrings
- internal validation and Codex workflow guidance

Build locally with:

```bash
python -m mkdocs build --strict
```

## Development

Run the default local checks with:

```bash
python -m pytest -q
python -m ruff check .
python -m pyrefly check src/linkedin_web_scraper/config/job_scraper_config.py src/linkedin_web_scraper/config/job_scraper_advanced_config.py src/linkedin_web_scraper/config/job_scraper_config_factory.py src/linkedin_web_scraper/config/openai.py src/linkedin_web_scraper/config/options.py src/linkedin_web_scraper/application/daily_scrape_service.py src/linkedin_web_scraper/application/linkedin_job_scraper.py src/linkedin_web_scraper/domain/job_data_cleaner.py src/linkedin_web_scraper/domain/job_title_classifier.py src/linkedin_web_scraper/infra/logging.py src/linkedin_web_scraper/infra/paths.py src/linkedin_web_scraper/infra/http/policy.py src/linkedin_web_scraper/infra/http/utils.py src/linkedin_web_scraper/infra/http/job_scraper.py src/linkedin_web_scraper/infra/openai/models.py src/linkedin_web_scraper/infra/openai/openai_handler.py src/linkedin_web_scraper/infra/openai/job_description_processor.py
```

## License

This project is licensed under the MIT License.
