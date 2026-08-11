from __future__ import annotations

from dataclasses import dataclass

from linkedin_web_scraper.config.anthropic import DEFAULT_ANTHROPIC_MODEL
from linkedin_web_scraper.config.job_scraper_advanced_config import JobScraperAdvancedConfig
from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL
from linkedin_web_scraper.config.options import EnrichmentProvider, RemoteType, TimePosted


def _default_enrichment_model(provider: EnrichmentProvider) -> str:
    """Return the provider-appropriate default enrichment model."""
    return (
        DEFAULT_ANTHROPIC_MODEL
        if provider == EnrichmentProvider.ANTHROPIC
        else DEFAULT_OPENAI_MODEL
    )


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


def _normalize_enrichment_provider(value: str | EnrichmentProvider) -> EnrichmentProvider:
    """Normalize user-facing enrichment-provider values to the enum form."""
    if isinstance(value, EnrichmentProvider):
        return value
    return EnrichmentProvider(value.upper())


@dataclass(slots=True)
class JobScraperConfig:
    """Typed runtime configuration for a single LinkedIn scrape."""

    position: str
    location: str
    enrichment_provider: EnrichmentProvider = EnrichmentProvider.NONE
    enrichment_required: bool = False
    enrichment_model: str = ""
    time_posted: TimePosted = TimePosted.DAY
    remote: RemoteType = RemoteType.ALL
    distance: int = 10
    advanced_config: JobScraperAdvancedConfig | None = None

    def __post_init__(self) -> None:
        self.position = self.position.strip()
        self.location = self.location.strip()
        self.enrichment_provider = _normalize_enrichment_provider(self.enrichment_provider)
        default_model = _default_enrichment_model(self.enrichment_provider)
        self.enrichment_model = (self.enrichment_model or default_model).strip() or default_model
        self.time_posted = _normalize_time_posted(self.time_posted)
        self.remote = _normalize_remote_type(self.remote)
        self.distance = int(self.distance)

    def __str__(self) -> str:
        return (
            "JobScraperConfig("
            f"position={self.position}, location={self.location}, "
            f"enrichment_provider={self.enrichment_provider}, "
            f"enrichment_required={self.enrichment_required}, "
            f"enrichment_model={self.enrichment_model}, "
            f"time_posted={self.time_posted}, remote={self.remote}, distance={self.distance})"
        )
