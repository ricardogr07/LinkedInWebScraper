# Configuration

This project supports typed programmatic config and TOML-driven runtime config.

## Programmatic Library Config

### `JobScraperConfig`

`JobScraperConfig` captures the runtime inputs for a single scrape:

- `position`: job title or search phrase
- `location`: LinkedIn location text
- `enrichment_provider`: `none`, `openai`, or `anthropic`, default `none`
- `enrichment_model`: model name for the selected provider, defaults to `gpt-4o-mini` for OpenAI and `claude-haiku-4-5-20251001` for Anthropic
- `time_posted`: `TimePosted` enum value or matching string
- `remote`: `RemoteType` enum value or matching string
- `distance`: search radius
- `advanced_config`: optional `JobScraperAdvancedConfig` overrides

### `JobScraperAdvancedConfig`

Use it for optional overrides such as:

- `LOCATION_MAPPING`
- `KEYWORDS`
- `SKILLS_CATEGORIES`

### Runtime Enums

- `TimePosted`: `ALL`, `MONTH`, `WEEK`, `DAY`
- `RemoteType`: `ALL`, `ON-SITE`, `REMOTE`, `HYBRID`

## Runtime TOML Config

The tracked template is `runtime.example.toml`. A real `runtime.toml` can define:

```toml
[logging]
level = "INFO"
file_name = "main.log"

[storage]
file_name = "linkedin_jobs.sqlite"
state_dir = "artifacts/state"

[scrape.once]
position = "Data Scientist"
location = "Monterrey"
enrichment_provider = "none"
enrichment_model = "gpt-4o-mini"
time_posted = "DAY"
remote_types = ["REMOTE", "HYBRID", "ON-SITE"]
file_name = "LinkedIn_Jobs_Data_Scientist_Monterrey.csv"
output_dir = "artifacts/jobs"
append = true

[scrape.daily]
cities = ["Monterrey", "Guadalajara", "Mexico City"]
position = "Data Scientist"
enrichment_provider = "none"
enrichment_model = "gpt-4o-mini"
time_posted = "DAY"
output_dir = "artifacts/jobs"
combined_file_name = "LinkedIn_Jobs_Data_Scientist_Mexico.csv"

[export]
run_id = ""
file_name = "linkedin_jobs_export.csv"
output_dir = "artifacts/jobs"
```

## CLI Override Precedence

The runtime precedence is:

1. CLI flags
2. environment overrides
3. TOML file values
4. code defaults

Supported env overrides include:

- `LINKEDIN_WEB_SCRAPER_CONFIG`
- `LINKEDIN_WEB_SCRAPER_LOG_LEVEL`
- `LINKEDIN_WEB_SCRAPER_LOG_FILE`
- `LINKEDIN_WEB_SCRAPER_STORAGE_URL`
- `LINKEDIN_WEB_SCRAPER_STORAGE_FILE`
- `LINKEDIN_WEB_SCRAPER_STATE_DIR`
- `LINKEDIN_WEB_SCRAPER_OUTPUT_DIR`
- `LINKEDIN_WEB_SCRAPER_ENRICHMENT_PROVIDER`
- `LINKEDIN_WEB_SCRAPER_ENRICHMENT_REQUIRED`
- `LINKEDIN_WEB_SCRAPER_ENRICHMENT_MODEL`

## Enrichment Runtime Behavior

Enrichment is optional and provider-selectable through `enrichment_provider` (`none`, `openai`, or `anthropic`).

- Install `LinkedInWebScraper[openai]` or `LinkedInWebScraper[anthropic]` to match the selected provider
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in the environment, matching the selected provider
- Keep secrets out of TOML and out of the repo
- By default, enrichment setup or request failures fall back to the non-enriched dataset; set `enrichment_required = true` to fail the run instead
- Enriched rows include audit fields such as `EnrichmentModel`, `EnrichmentResponseId`, and `EnrichmentRawPayload`

## Artifact And State Paths

Managed defaults resolve under `artifacts/`:

- bare CSV file names -> `artifacts/jobs/`
- bare log file names -> `artifacts/logs/`
- bare SQLite file names -> `artifacts/state/`

Explicit absolute paths and explicit nested relative paths are preserved.

## Storage Model

SQLite persistence is enabled by default for CLI and `DailyScrapeService` workflows.

- `scrape_runs` stores run lifecycle metadata
- `jobs` stores the latest canonical job attributes
- `job_snapshots` stores the run-level dataframe payload
- `job_enrichments` stores structured OpenAI audit data when present
- CSV exports are downstream artifacts written from persisted data

Use `build_sqlite_storage_url()` for a managed default URL, or inject `SQLiteScrapeStorage(storage_url=...)` into `DailyScrapeService` when you need a custom local path or DSN.

### mssql / Azure SQL

`SQLiteScrapeStorage` runs against any SQLAlchemy-supported dialect, not only SQLite.
Point it at Azure SQL (or any mssql server) by setting `LINKEDIN_WEB_SCRAPER_STORAGE_URL`
to a `mssql+pyodbc://` URL, or by passing that URL as `runtime_config.storage.url` /
`storage_url=`. Install the `pyodbc` driver dependency with:

```bash
pip install LinkedInWebScraper[mssql]
```

Text columns use SQLAlchemy's generic `Unicode`/`UnicodeText` types so mssql renders
them as `NVARCHAR`, keeping non-ASCII text (Spanish job postings, for example)
round-tripping correctly. The engine is created with `pool_pre_ping=True` so a stale
connection, for example an Azure SQL serverless tier resuming from auto-pause, is
retried transparently instead of surfacing as a connection error.

`Base.metadata.create_all()` provisions the schema on first use; there is no Alembic
migration path yet, schema changes require a fresh database or a hand-run migration.

## Root Runtime Scripts

`main.py` and `process_ds_jobs.py` remain available as direct runtime entrypoints for the daily and once workflows.
