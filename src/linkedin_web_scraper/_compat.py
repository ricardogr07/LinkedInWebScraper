"""Compatibility helpers for deprecated legacy namespaces."""

from __future__ import annotations

import warnings


def warn_legacy_namespace(legacy_namespace: str) -> None:
    """Warn when callers import from a deprecated legacy namespace."""
    warnings.warn(
        (
            f"`{legacy_namespace}` is deprecated and will be removed in a future major release. "
            "Import from `linkedin_web_scraper` instead."
        ),
        DeprecationWarning,
        stacklevel=2,
    )
