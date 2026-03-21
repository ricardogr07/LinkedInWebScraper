# Configuration

This project currently uses programmatic configuration objects. TOML-driven runtime configuration is planned later, but the library surface today is centered on typed Python models and injectable runtime services.

## `JobScraperConfig`

`JobScraperConfig` captures the runtime inputs for a single scrape:

- `position`: job title or search phrase.
- `location`: LinkedIn location text.
- `openai_enabled`: enable optional description enrichment.
- `openai_model`: the model name used for optional OpenAI enrichment. Defaults to `gpt-4o-mini`.
- `time_posted`: `TimePosted` enum value or a matching string.
- `remote`: `RemoteType` enum value or a matching string.
- `distance`: search radius in miles.
- `advanced_config`: optional `JobScraperAdvancedConfig` overrides.

String values for `time_posted` and `remote` are normalized into enums during initialization. `openai_model` is stripped and normalized to the default model when blank.

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

## OpenAI Runtime Behavior

OpenAI support is optional.

- Install the optional extra before enabling enrichment: `pip install LinkedInWebScraper[openai]`
- Set `OPENAI_API_KEY` in the environment before running the scraper
- The library does not call `dotenv` during import or runtime setup
- Enrichment uses the configured `openai_model` and is best-effort; failures fall back to the non-enriched dataset
- Enriched rows include `OpenAIModel`, `OpenAIResponseId`, and `OpenAIRawPayload` for audit/debug visibility

## Artifact And State Paths

By default, managed outputs resolve under `artifacts/`:

- bare CSV file names go to `artifacts/jobs/`
- bare log file names go to `artifacts/logs/`
- bare SQLite/state file names go to `artifacts/state/`

Explicit absolute paths and explicit nested relative paths are preserved as given.

## Current Storage Model

Phase 6 uses SQLite-backed persistence by default through `DailyScrapeService`.

- `scrape_runs` tracks run lifecycle metadata and output paths
- `jobs` stores the latest canonical attributes for each `JobID`
- `job_snapshots` stores the row-level dataframe payload for each run
- `job_enrichments` stores structured OpenAI audit data when enrichment is present
- CSV exports are written from persisted run data after storage succeeds

Use `build_sqlite_storage_url()` for a managed default SQLite URL, or inject `SQLiteScrapeStorage(storage_url=...)` into `DailyScrapeService` when you need a custom local database path.

## Daily Runs

`DailyScrapeService` coordinates a multi-city run across the default remote variants:

- `REMOTE`
- `HYBRID`
- `ON-SITE`

You can override the city list, position, output directory, combined output file name, or the injected storage adapter without changing the lower-level scraper classes.

## Migration Notes

- Import from `linkedin_web_scraper` for new work.
- Keep legacy imports only when validating compatibility or supporting older callers.
- `main.py` and the example scripts remain part of the compatibility surface until a later major-version cleanup.
