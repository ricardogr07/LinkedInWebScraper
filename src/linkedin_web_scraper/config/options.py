from __future__ import annotations

from enum import StrEnum


class TimePosted(StrEnum):
    """Supported LinkedIn time-posted filter values."""

    ALL = "ALL"
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"


class RemoteType(StrEnum):
    """Supported LinkedIn remote-work filter values."""

    ALL = "ALL"
    ON_SITE = "ON-SITE"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"


class EnrichmentProvider(StrEnum):
    """Supported job-description enrichment providers."""

    NONE = "NONE"
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"


__all__ = ["EnrichmentProvider", "RemoteType", "TimePosted"]
