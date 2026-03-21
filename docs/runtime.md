# Runtime and Deployment

## CLI Commands

The canonical CLI entrypoint is:

```bash
linkedin-webscraper <command>
```

Supported commands:

- `scrape once`: single-location scrape with persistence and CSV export
- `scrape daily`: multi-city daily scrape with persistence and CSV export
- `export`: export a persisted run from SQLite to CSV

Examples:

```bash
linkedin-webscraper scrape once --config runtime.toml
linkedin-webscraper scrape daily --config runtime.toml
linkedin-webscraper export --config runtime.toml --run-id <run-id>
```

## Dry Run

Use `--dry-run` to validate the resolved runtime plan without hitting LinkedIn:

```bash
linkedin-webscraper scrape once --config runtime.toml --dry-run
linkedin-webscraper scrape daily --config runtime.toml --dry-run
linkedin-webscraper export --config runtime.toml --run-id <run-id> --dry-run
```

Dry run prints the resolved command, key runtime inputs, output path, and storage URL.

## Compatibility Wrappers

These scripts remain valid during the migration:

- `python main.py` -> defaults to `scrape daily`
- `python process_ds_jobs.py` -> defaults to `scrape once`

They delegate to the canonical package CLI instead of carrying separate runtime logic.

## Runtime Config File

Use `runtime.example.toml` as the starting point for a local or scheduled `runtime.toml`.

Typical workflow:

```bash
copy runtime.example.toml runtime.toml
linkedin-webscraper scrape daily --config runtime.toml
```

You can also point to a config path through `LINKEDIN_WEB_SCRAPER_CONFIG`.

## Docker

The repo includes a slim `Dockerfile` and `.dockerignore`.

Build the image:

```bash
docker build -t linkedin-webscraper .
```

Build with the optional OpenAI extra:

```bash
docker build --build-arg INSTALL_EXTRAS=openai -t linkedin-webscraper:openai .
```

Run with mounted artifacts and runtime config:

```bash
docker run --rm \
  -v ${PWD}/artifacts:/app/artifacts \
  -v ${PWD}/runtime.toml:/app/runtime.toml \
  -e LINKEDIN_WEB_SCRAPER_CONFIG=/app/runtime.toml \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  linkedin-webscraper:openai scrape daily
```

## State And Artifacts

Default managed locations inside the container and local runtime are the same:

- `artifacts/jobs`
- `artifacts/logs`
- `artifacts/state`

That keeps local runs, containers, and future CI schedulers on the same path contract.

