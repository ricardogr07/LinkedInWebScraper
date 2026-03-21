# Tools and Commands

This page lists the exact local commands and tool statuses that matter for development in this repo.

## Repo Commands

### `test`
- Command: `python -m pytest -q`
- Purpose: run the default offline test suite.
- Status: `ready`

### `lint`
- Command: `python -m ruff check .`
- Purpose: run repository lint checks.
- Status: `ready`

### `format`
- Command: `python -m ruff format .`
- Purpose: apply repository formatting rules.
- Status: `ready`

### `type_bootstrap`
- Command: `python -m pyrefly check src/linkedin_web_scraper/config/job_scraper_config.py src/linkedin_web_scraper/config/job_scraper_advanced_config.py src/linkedin_web_scraper/config/job_scraper_config_factory.py src/linkedin_web_scraper/config/openai.py src/linkedin_web_scraper/config/storage.py src/linkedin_web_scraper/config/options.py src/linkedin_web_scraper/config/runtime.py src/linkedin_web_scraper/application/daily_scrape_service.py src/linkedin_web_scraper/application/linkedin_job_scraper.py src/linkedin_web_scraper/application/storage.py src/linkedin_web_scraper/application/runtime_runner.py src/linkedin_web_scraper/domain/job_data_cleaner.py src/linkedin_web_scraper/domain/job_title_classifier.py src/linkedin_web_scraper/infra/logging.py src/linkedin_web_scraper/infra/paths.py src/linkedin_web_scraper/infra/http/policy.py src/linkedin_web_scraper/infra/http/utils.py src/linkedin_web_scraper/infra/http/job_scraper.py src/linkedin_web_scraper/infra/openai/models.py src/linkedin_web_scraper/infra/openai/openai_handler.py src/linkedin_web_scraper/infra/openai/job_description_processor.py src/linkedin_web_scraper/infra/storage/models.py src/linkedin_web_scraper/infra/storage/sqlite.py`
- Purpose: run the current canonical-package Pyrefly seam across config, application orchestration, domain logic, and core infrastructure helpers.
- Status: `incremental`

### `docs`
- Command: `python -m mkdocs build --strict`
- Purpose: build user-facing and internal docs and fail on nav or markdown errors.
- Status: `ready`

### `build`
- Command: `python -m build --no-isolation`
- Purpose: build the source distribution and wheel from the current working tree.
- Status: `ready`

### `smoke_examples`
- Command: `python -m pytest -q tests/test_example_smoke.py tests/test_main_smoke.py`
- Purpose: verify the example and daily-run orchestration paths stay intact.
- Status: `ready`

### `tox_all`
- Command: `python -m tox`
- Purpose: run the tox matrix with missing interpreters skipped.
- Status: `ready`

## Local Tool Status

### `git`
- Check: `git status --short`
- Review helper: `git diff --stat`
- Status: `available_now`

### `python`
- Check: `python --version`
- Status: `available_now`

### `gh`
- Check: `gh auth status`
- Status: `blocked_or_misconfigured`
- Current note: the CLI is installed, but the active auth token is invalid in this environment.

### `docker`
- Check: `docker version`
- Status: `blocked_or_misconfigured`
- Current note: the CLI is installed, but the daemon or config are not currently usable from this session.

### `codex`
- Check: `codex --help`
- Status: `available_now`
- Current note: the direct executable exists, but some shells may hit execution-policy issues with wrapper scripts. Prefer documented Codex workflows over local shell assumptions.

## Why The Commands Use `python -m`
- The repo toolchain is more reliable when invoked through the active Python interpreter.
- It avoids dependence on whether script shims are on `PATH`.



