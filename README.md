# LinkedInWebScraper

[![CI](https://github.com/ricardogr07/LinkedInWebScraper/actions/workflows/ci.yml/badge.svg)](https://github.com/ricardogr07/LinkedInWebScraper/actions/workflows/ci.yml)
[![Docs](https://github.com/ricardogr07/LinkedInWebScraper/actions/workflows/docs.yml/badge.svg)](https://github.com/ricardogr07/LinkedInWebScraper/actions/workflows/docs.yml)
[![Release](https://github.com/ricardogr07/LinkedInWebScraper/actions/workflows/release.yml/badge.svg)](https://github.com/ricardogr07/LinkedInWebScraper/actions/workflows/release.yml)
[![PyPI version](https://img.shields.io/pypi/v/LinkedInWebScraper.svg)](https://pypi.org/project/LinkedInWebScraper/)
[![Python versions](https://img.shields.io/pypi/pyversions/LinkedInWebScraper.svg)](https://pypi.org/project/LinkedInWebScraper/)
[![License](https://img.shields.io/pypi/l/LinkedInWebScraper.svg)](https://github.com/ricardogr07/LinkedInWebScraper/blob/main/LICENSE)

LinkedInWebScraper is a production-minded Python library and scheduled job runner for collecting LinkedIn job listings, normalizing the data, persisting run history, and exporting reusable datasets.

## Highlights

- Canonical package namespace under `linkedin_web_scraper`
- Typed programmatic config for single scrapes and TOML runtime config for CLI and scheduled runs
- Managed artifacts under `artifacts/jobs`, `artifacts/logs`, and `artifacts/state`
- SQLite-backed persistence through a clean application storage port
- Package CLI with `scrape once`, `scrape daily`, `export`, and `--dry-run`
- Optional OpenAI enrichment built on the current Responses API
- Runnable examples under `examples/`
- Auto release automation that waits for green CI and Docs runs on `main`

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

Run the local gate before risky pushes or merges:

```bash
python -m tox -e preflight
```

For a faster smoke-only path:

```bash
python -m tox -e smoke
```

The detailed validation matrix and release flow live in `docs/development/validation.md` and `docs/development/release-and-automation.md`.

## License

This project is licensed under the MIT License.
