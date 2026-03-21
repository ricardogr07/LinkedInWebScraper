# LinkedInWebScraper

LinkedInWebScraper is a production-minded Python library and scheduled job runner for collecting LinkedIn job listings, normalizing the data, persisting run history, and exporting reusable datasets.

## Highlights

- Canonical package namespace under `linkedin_web_scraper`
- Typed programmatic config for single scrapes and TOML runtime config for CLI and scheduled runs
- Managed artifacts under `artifacts/jobs`, `artifacts/logs`, and `artifacts/state`
- SQLite-backed persistence through a clean application storage port
- Package CLI with `scrape once`, `scrape daily`, `export`, and `--dry-run`
- Optional OpenAI enrichment built on the current Responses API
- Runnable examples under `examples/`

## Install

```bash
pip install LinkedInWebScraper
pip install LinkedInWebScraper[openai]
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

jobs = LinkedInJobScraper(logger=logger, config=config).run()
print(jobs.head())
```

## Examples

Run the example scripts from `examples/`:

```bash
python examples/example.py
python examples/example_advanced_config.py
python examples/example_openai.py
```

The OpenAI example requires `OPENAI_API_KEY` in the environment.

## CLI Runtime

```bash
linkedin-webscraper scrape once --dry-run
linkedin-webscraper scrape daily
linkedin-webscraper export --run-id <run-id>
```

Use `runtime.example.toml` as the template for a real `runtime.toml`. The root runtime scripts remain available for the daily and once workflows:

```bash
python main.py
python process_ds_jobs.py
```

## Docs

- [Getting Started](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Runtime and Deployment](docs/runtime.md)
- [Release and Automation](docs/development/release-and-automation.md)
- [Validation](docs/development/validation.md)
- [API Reference](docs/api.md)

## Development

```bash
python -m pytest -q
python -m ruff check .
python -m mkdocs build --strict
python -m pyrefly check src/linkedin_web_scraper/config/job_scraper_config.py src/linkedin_web_scraper/config/job_scraper_advanced_config.py src/linkedin_web_scraper/config/job_scraper_config_factory.py src/linkedin_web_scraper/config/openai.py src/linkedin_web_scraper/config/storage.py src/linkedin_web_scraper/config/options.py src/linkedin_web_scraper/config/runtime.py src/linkedin_web_scraper/application/daily_scrape_service.py src/linkedin_web_scraper/application/linkedin_job_scraper.py src/linkedin_web_scraper/application/storage.py src/linkedin_web_scraper/application/runtime_runner.py src/linkedin_web_scraper/domain/job_data_cleaner.py src/linkedin_web_scraper/domain/job_title_classifier.py src/linkedin_web_scraper/infra/logging.py src/linkedin_web_scraper/infra/paths.py src/linkedin_web_scraper/infra/http/policy.py src/linkedin_web_scraper/infra/http/utils.py src/linkedin_web_scraper/infra/http/job_scraper.py src/linkedin_web_scraper/infra/openai/models.py src/linkedin_web_scraper/infra/openai/openai_handler.py src/linkedin_web_scraper/infra/openai/job_description_processor.py src/linkedin_web_scraper/infra/storage/models.py src/linkedin_web_scraper/infra/storage/sqlite.py
```

## License

This project is licensed under the MIT License.
