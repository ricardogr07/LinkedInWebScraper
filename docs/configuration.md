# Configuration

This project currently uses programmatic configuration objects. TOML-driven runtime configuration is planned later, but the library surface today is centered on typed Python models.

## `JobScraperConfig`

`JobScraperConfig` captures the runtime inputs for a single scrape:

- `position`: job title or search phrase.
- `location`: LinkedIn location text.
- `openai_enabled`: enable optional description enrichment.
- `time_posted`: `TimePosted` enum value or a matching string.
- `remote`: `RemoteType` enum value or a matching string.
- `distance`: search radius in miles.
- `advanced_config`: optional `JobScraperAdvancedConfig` overrides.

String values for `time_posted` and `remote` are normalized into enums during initialization.

## `JobScraperAdvancedConfig`

`JobScraperAdvancedConfig` provides optional overrides for:

- `LOCATION_MAPPING`: custom location normalization rules.
- `KEYWORDS`: title-classification keywords.
- `SKILLS_CATEGORIES`: enrichment output categories.

The model copies mutable input collections so callers can safely reuse their original data structures after configuration is created.

## Runtime Enums

- `TimePosted`: `ALL`, `MONTH`, `WEEK`, `DAY`
- `RemoteType`: `ALL`, `ON-SITE`, `REMOTE`, `HYBRID`

Use the enums directly in new code when possible.

## Artifact Paths

By default, managed outputs resolve under `artifacts/`:

- bare CSV file names go to `artifacts/jobs/`
- bare log file names go to `artifacts/logs/`

Explicit absolute paths and explicit nested relative paths are preserved as given.

## Daily Runs

`DailyScrapeService` coordinates a multi-city run across the default remote variants:

- `REMOTE`
- `HYBRID`
- `ON-SITE`

You can override the city list, position, output directory, and combined output file name without changing the lower-level scraper classes.
