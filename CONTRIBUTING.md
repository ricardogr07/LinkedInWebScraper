# Contributing

Thanks for considering a contribution to LinkedInWebScraper. This is a
solo-maintained project, so keep changes focused and small.

## Setup

```bash
pip install -e .[dev]
```

## Preflight gate

Before opening a PR, run the tox preflight environment. It runs the full
test suite, lint, format check, and type check, the same checks CI runs:

```bash
python -m tox -e preflight
```

A PR is not ready for review until `tox -e preflight` passes locally.

## Pull requests

- One logical change per PR.
- Add or update tests for behavior changes.
- Update docs (`README.md`, `docs/`) if user-facing behavior changes.
- Keep commit messages clear; no AI attribution trailers.

## Reporting bugs / requesting features

Use the issue templates under `.github/ISSUE_TEMPLATE/`.
