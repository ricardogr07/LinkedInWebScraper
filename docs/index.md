# LinkedInWebScraper

LinkedInWebScraper provides a reusable workflow for scraping LinkedIn job listings, normalizing the output, persisting run history, and exporting datasets that can be rerun safely over time.

## What It Does

- Scrapes LinkedIn search result pages and job detail pages
- Cleans and normalizes job metadata such as locations, job IDs, and job-detail fields
- Supports daily multi-city export workflows through `DailyScrapeService`
- Writes managed artifacts under `artifacts/jobs`, `artifacts/logs`, and `artifacts/state`
- Persists run history to SQLite through a clean application-layer storage port
- Keeps OpenAI enrichment isolated behind an optional runtime path and package extra

## Architecture

The canonical package is `linkedin_web_scraper` and is organized into:

- `config` for typed runtime inputs and constants
- `application` for orchestration services and storage contracts
- `domain` for cleaning and classification logic
- `infra` for HTTP, logging, path resolution, optional OpenAI, SQLite storage, and CSV helpers
- `interfaces` for CLI entrypoints

Legacy namespaces such as `LinkedInWebScraper`, `Utils`, and `OpenAIHandler` still work through compatibility wrappers, but new code should import from `linkedin_web_scraper`.

## Runtime Defaults

- Bare log filenames resolve under `artifacts/logs`
- Bare CSV export filenames resolve under `artifacts/jobs`
- Bare SQLite/state filenames resolve under `artifacts/state`
- `DailyScrapeService` persists runs to `artifacts/state/linkedin_jobs.sqlite` by default
- OpenAI enrichment is optional and requires the `openai` extra plus `OPENAI_API_KEY`

## Next Steps

- Follow [Getting Started](getting-started.md) for a local scrape flow
- Use [Configuration](configuration.md) to understand runtime options, storage defaults, and artifact paths
- See [API Reference](api.md) for generated reference documentation
