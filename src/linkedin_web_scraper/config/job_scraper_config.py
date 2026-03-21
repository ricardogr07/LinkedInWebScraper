from __future__ import annotations

from dataclasses import dataclass

from linkedin_web_scraper.config.job_scraper_advanced_config import JobScraperAdvancedConfig
from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL
from linkedin_web_scraper.config.options import RemoteType, TimePosted


def _normalize_time_posted(value: str | TimePosted) -> TimePosted:
    """Normalize user-facing time-posted values to the enum form."""
    if isinstance(value, TimePosted):
        return value
    return TimePosted(value.upper())


def _normalize_remote_type(value: str | RemoteType) -> RemoteType:
    """Normalize user-facing remote-type values to the enum form."""
    if isinstance(value, RemoteType):
        return value
    return RemoteType(value.upper())


@dataclass(slots=True)
class JobScraperConfig:
    """Typed runtime configuration for a single LinkedIn scrape."""

    position: str
    location: str
    openai_enabled: bool = False
    openai_model: str = DEFAULT_OPENAI_MODEL
    time_posted: TimePosted = TimePosted.DAY
    remote: RemoteType = RemoteType.ALL
    distance: int = 10
    advanced_config: JobScraperAdvancedConfig | None = None

    def __post_init__(self) -> None:
        self.position = self.position.strip()
        self.location = self.location.strip()
        self.openai_model = (
            self.openai_model or DEFAULT_OPENAI_MODEL
        ).strip() or DEFAULT_OPENAI_MODEL
        self.time_posted = _normalize_time_posted(self.time_posted)
        self.remote = _normalize_remote_type(self.remote)
        self.distance = int(self.distance)

    def __str__(self) -> str:
        return (
            "JobScraperConfig("
            f"position={self.position}, location={self.location}, "
            f"openai_enabled={self.openai_enabled}, openai_model={self.openai_model}, "
            f"time_posted={self.time_posted}, remote={self.remote}, distance={self.distance})"
        )
