# LinkedInWebScraper

LinkedInWebScraper provides a reusable workflow for scraping LinkedIn job listings, normalizing the output, and exporting datasets that can be rerun safely over time.

## What It Does

- Scrapes LinkedIn search result pages and job detail pages
- Cleans and normalizes job metadata such as locations and job IDs
- Supports daily multi-city export workflows through `DailyScrapeService`
- Writes managed artifacts under `artifacts/jobs` and `artifacts/logs` by default
- Keeps OpenAI enrichment isolated behind an optional runtime path

## Package Shape

The canonical package is `linkedin_web_scraper`.

Legacy namespaces such as `LinkedInWebScraper`, `Utils`, and `OpenAIHandler` still work through compatibility wrappers, but new code should import from `linkedin_web_scraper`.

## Runtime Defaults

- Bare log filenames resolve under `artifacts/logs`
- Bare CSV export filenames resolve under `artifacts/jobs`
- Explicit absolute or nested relative paths bypass the managed artifact directories

## Next Steps

- Follow [Getting Started](getting-started.md) for a local scrape flow
- Use [Configuration](configuration.md) to understand runtime options and artifact paths
- See [API Reference](api.md) for generated reference documentation
