# Release and Automation

This repository ships four GitHub Actions workflows that cover validation, docs publishing, package publishing, and the scheduled daily scrape.

## Workflow Inventory

- `ci.yml`: runs the tox matrix on every push and pull request.
- `docs.yml`: builds MkDocs and deploys the generated site to GitHub Pages on pushes to `main` and on manual dispatch.
- `release.yml`: auto-triggers from successful CI and Docs runs on `main`, creates the GitHub Release object, and publishes to PyPI with trusted publishing.
- `daily-scrape.yml`: runs the scheduled multi-city scrape, preserves SQLite state on the `data` branch, uploads artifacts, and opens a failure issue when the automation breaks.

## One-Time GitHub Setup

### GitHub Pages

- In repository Settings > Pages, set the source to GitHub Actions before the first docs deployment.
- Keep `mkdocs.yml` aligned with the published Pages URL.

### Trusted Publishing

- Create a GitHub environment named `pypi` if you want environment-level approval or separation.
- Configure a trusted publisher in PyPI so it trusts `.github/workflows/release.yml` from this repository.
- No PyPI username/password or API token secret is required when trusted publishing is enabled.
- If you choose token-based publishing instead, that is a separate workflow path.

Recommended release posture:

- use `workflow_dispatch` for controlled PyPI recovery or manual release runs from `main`
- let the `workflow_run` path publish automatically when the version in `pyproject.toml` increases and both CI and Docs are green on `main`
- create the GitHub Release object before the PyPI publish step

### Scheduled Runtime

- The scheduled scrape reads `.github/runtime/daily.toml`.
- Optional OpenAI use still requires `OPENAI_API_KEY` as a repository secret.
- The workflow keeps OpenAI disabled by default in TOML so the scheduled run stays resilient without external API dependencies.

### Repository Permissions

- Allow GitHub Actions to push to the `data` branch so the scheduled workflow can commit state.
- Keep the `contents: write` and `issues: write` permissions in the workflow file.

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

`release.yml` now supports two release paths:

- `workflow_run` on `CI` and `Docs` completions for automatic PyPI releases from `main`
- `workflow_dispatch` for controlled PyPI recovery or release reruns

The automated release job sequence is:

1. confirm the current commit is on `main` and both CI and Docs succeeded for the same SHA
2. read the version from `pyproject.toml` and compare it with the latest published release
3. skip if the version is not newer or the tag already exists
4. build the sdist and wheel through `tox -e build`
5. create the GitHub Release object and upload the built wheel and sdist
6. publish the same built artifacts to PyPI with trusted publishing

Manual dispatch uses the same artifact flow, but it still respects the version gate so duplicate releases are skipped.

### Rollback

PyPI does not allow overwriting a released version.

Rollback guidance:

- if a release is bad, yank it on PyPI
- fix the issue in the repo
- cut a new version and publish that replacement
- keep the GitHub Release notes clear about the superseding version

## Daily Automation

`daily-scrape.yml` runs at `30 12 * * *`, which is 12:30 UTC every day.

The workflow sequence is:

1. install the package with the optional OpenAI extra available
2. attach a `data` branch worktree
3. restore the previous SQLite state from the `data-latest` release asset; a run refuses to start fresh unless it positively confirms the asset is absent and was dispatched with `allow_fresh_state=true` (first-run bootstrap only)
4. initialize the SQLite schema before the scrape
5. run a CLI dry run for visibility
6. run `linkedin-webscraper scrape daily --config .github/runtime/daily.toml`
7. upload `artifacts/state/linkedin_jobs.sqlite` back to the `data-latest` release with `--clobber`
8. copy current CSV exports to both `data/exports/latest` and `data/exports/YYYY-MM-DD`
9. commit and push the export data back to `data`
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
- The persistence contract for GitHub-hosted automation: the canonical `linkedin_jobs.sqlite` lives as an asset on the rolling `data-latest` release (2 GiB per-file limit, kept out of git history); CSV exports live on the `data` branch. A future cloud database can replace the release asset without changing the CLI surface.
- Rollback for state: every run also uploads `artifacts/state` as a workflow artifact with 14-day retention; re-upload a prior day's database to the `data-latest` release to roll back.
- Use `python -m tox -e preflight` before risky pushes or merges. That local gate runs the same smoke, lint, type, docs, and build checks that the repo expects before release work.