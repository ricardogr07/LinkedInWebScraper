# Configuration

This project now supports both typed programmatic config and TOML-driven runtime config.

## Programmatic Library Config

### `JobScraperConfig`

`JobScraperConfig` captures the runtime inputs for a single scrape:

- `position`: job title or search phrase
- `location`: LinkedIn location text
- `openai_enabled`: enable optional description enrichment
- `openai_model`: model name for optional OpenAI enrichment, default `gpt-4o-mini`
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
openai_enabled = false
openai_model = "gpt-4o-mini"
time_posted = "DAY"
remote_types = ["REMOTE", "HYBRID", "ON-SITE"]
file_name = "LinkedIn_Jobs_Data_Scientist_Monterrey.csv"
output_dir = "artifacts/jobs"
append = true

[scrape.daily]
cities = ["Monterrey", "Guadalajara", "Mexico City"]
position = "Data Scientist"
openai_enabled = false
openai_model = "gpt-4o-mini"
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
- `LINKEDIN_WEB_SCRAPER_OPENAI_ENABLED`
- `LINKEDIN_WEB_SCRAPER_OPENAI_MODEL`

## OpenAI Runtime Behavior

OpenAI support remains optional.

- Install `LinkedInWebScraper[openai]`
- Set `OPENAI_API_KEY` in the environment
- Keep secrets out of TOML and out of the repo
- Enrichment setup or request failures fall back to the non-enriched dataset
- Enriched rows include audit fields such as `OpenAIModel`, `OpenAIResponseId`, and `OpenAIRawPayload`

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

## Compatibility Notes

- New code should import from `linkedin_web_scraper`
- Runtime TOML is for CLI and scheduled jobs, not required for library use
- `main.py` and `process_ds_jobs.py` remain compatibility wrappers over the canonical CLI/service layer
