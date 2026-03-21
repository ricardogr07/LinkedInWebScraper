# LinkedInWebScraper

LinkedInWebScraper is a production-minded Python library and daily job runner for collecting LinkedIn job listings, normalizing the results, and exporting datasets that are easy to reuse in analysis pipelines.

## Highlights

- Canonical package namespace under `linkedin_web_scraper`
- Typed scraper configuration for locations, remote modes, and time filters
- Durable CSV export flow with managed artifact directories under `artifacts/`
- Daily multi-city orchestration through `main.py` or `DailyScrapeService`
- Optional OpenAI enrichment path for description post-processing
- Backward-compatible legacy imports while the migration stays in place

## Installation

```bash
pip install LinkedInWebScraper
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
python -m pyrefly check src/linkedin_web_scraper/config/job_scraper_config.py src/linkedin_web_scraper/config/job_scraper_advanced_config.py src/linkedin_web_scraper/config/job_scraper_config_factory.py src/linkedin_web_scraper/config/options.py src/linkedin_web_scraper/application/daily_scrape_service.py src/linkedin_web_scraper/interfaces/cli/main.py src/linkedin_web_scraper/infra/logging.py src/linkedin_web_scraper/infra/paths.py src/linkedin_web_scraper/infra/http/policy.py
```

## OpenAI Enrichment

OpenAI-backed enrichment is optional at runtime. If you enable it, set `OPENAI_API_KEY` in your environment before running the scraper.

## License

This project is licensed under the MIT License.
