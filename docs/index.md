# LinkedInWebScraper

LinkedInWebScraper provides a reusable workflow for scraping LinkedIn job listings, normalizing the results, persisting run history, and exporting datasets that can be rerun safely over time.

## What It Does

- Scrapes LinkedIn search result pages and job detail pages
- Cleans and normalizes job metadata such as locations, job IDs, and extracted fields
- Supports single scrapes and daily multi-city runs
- Persists run history to SQLite through a clean application storage port
- Writes managed artifacts under `artifacts/jobs`, `artifacts/logs`, and `artifacts/state`
- Keeps OpenAI enrichment optional and isolated behind an extra plus runtime toggle
- Keeps runnable examples under `examples/`

## Runtime Surfaces

The project has two supported runtime modes:

- Programmatic library usage through `JobScraperConfig`, `LinkedInJobScraper`, and `DailyScrapeService`
- TOML-driven CLI usage through `linkedin-webscraper scrape once`, `scrape daily`, and `export`

The root scripts remain available for direct execution:

- `python main.py` -> default daily run
- `python process_ds_jobs.py` -> default single-location run

## Defaults

- Bare log filenames resolve under `artifacts/logs`
- Bare CSV filenames resolve under `artifacts/jobs`
- Bare SQLite filenames resolve under `artifacts/state`
- Default managed DB path is `artifacts/state/linkedin_jobs.sqlite`
- OpenAI enrichment requires the optional extra and `OPENAI_API_KEY`

## Next Steps

- Follow [Getting Started](getting-started.md) for library and CLI usage
- Use [Configuration](configuration.md) for config models, runtime TOML, and env overrides
- Use [Runtime and Deployment](runtime.md) for CLI, dry-run, and Docker workflows
- See [API Reference](api.md) for generated module documentation
