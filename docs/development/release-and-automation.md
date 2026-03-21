# Release and Automation

This repository ships four GitHub Actions workflows that cover validation, docs publishing, package publishing, and the scheduled daily scrape.

## Workflow Inventory

- `ci.yml`: runs the tox matrix on every push and pull request.
- `docs.yml`: builds MkDocs and deploys the generated site to GitHub Pages on pushes to `main` and on manual dispatch.
- `release.yml`: builds distributions and publishes them to TestPyPI and/or PyPI with trusted publishing.
- `daily-scrape.yml`: runs the scheduled multi-city scrape, preserves SQLite state on the `data` branch, uploads artifacts, and opens a failure issue when the automation breaks.

## Required Repository Settings

### GitHub Pages

- Set Pages to deploy from GitHub Actions.
- Keep `mkdocs.yml` aligned with the published Pages URL.

### Trusted Publishing

Create GitHub environments named `testpypi` and `pypi`, then configure trusted publishers in both package indexes so they trust `.github/workflows/release.yml` from this repository.

Recommended release posture:

- run the workflow manually against TestPyPI first
- publish to PyPI only after the TestPyPI install/import smoke passes
- use GitHub Releases for the final PyPI publish path

### Scheduled Runtime

- The scheduled scrape reads `.github/runtime/daily.toml`.
- Optional OpenAI use still requires `OPENAI_API_KEY` as a repository secret.
- The workflow keeps OpenAI disabled by default in TOML so the scheduled run stays resilient without external API dependencies.

## CI Flow

`ci.yml` is the push/PR gate.

It runs:

- `py311`, `py312`, `py313`, and `py314`
- `lint`
- `type`
- `docs`
- `build`

This keeps the local tox contract and the GitHub CI contract identical.

## Docs Publish Flow

`docs.yml` performs two jobs:

1. install the docs build dependencies and run `python -m mkdocs build --strict`
2. upload the `site/` artifact and deploy it with the GitHub Pages deployment actions

The workflow is intentionally limited to `main` pushes and manual dispatch so preview behavior stays on the normal PR checks instead of publishing every branch.

## Release Flow

`release.yml` supports two release paths:

- `workflow_dispatch` for `testpypi`, `pypi`, or `both`
- `release.published` for the final PyPI publish

The release job sequence is:

1. build the sdist and wheel through `tox -e build`
2. publish to TestPyPI when requested
3. publish to PyPI only when the PyPI path was requested and the TestPyPI job either succeeded or was intentionally skipped

### Rollback

PyPI does not allow overwriting a released version.

Rollback guidance:

- if a release is bad, yank it on PyPI/TestPyPI
- fix the issue in the repo
- cut a new version and publish that replacement
- keep the GitHub Release notes clear about the superseding version

## Daily Automation

`daily-scrape.yml` runs at `30 12 * * *`, which is 12:30 UTC every day.

The workflow sequence is:

1. install the package with the optional OpenAI extra available
2. attach a `data` branch worktree
3. restore the previous SQLite state from `data/state`
4. initialize the SQLite schema before the scrape
5. run a CLI dry run for visibility
6. run `linkedin-webscraper scrape daily --config .github/runtime/daily.toml`
7. copy `artifacts/state` back to `data/state`
8. copy current CSV exports to both `data/exports/latest` and `data/exports/YYYY-MM-DD`
9. commit and push the updated automation state back to `data`
10. upload workflow artifacts and summarize the run

### Failure Handling

The workflow includes:

- a dedicated concurrency group so two daily runs do not overlap
- artifact retention for 14 days
- an issue-based failure notification that opens or updates `[automation] Daily scrape failure`
- automatic closure of that issue once a later run succeeds

## Operating Notes

- Keep secrets out of TOML and out of the repo.
- If you enable OpenAI for scheduled runs later, do it by combining a repo secret with `openai_enabled = true` in `.github/runtime/daily.toml` or a workflow env override.
- The `data` branch is the current persistence contract for GitHub-hosted automation. A future cloud database can replace it without changing the CLI surface.