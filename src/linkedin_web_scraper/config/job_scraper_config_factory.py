from __future__ import annotations

from linkedin_web_scraper.config.job_scraper_advanced_config import JobScraperAdvancedConfig
from linkedin_web_scraper.config.job_scraper_config import (
    JobScraperConfig,
    _normalize_enrichment_provider,
    _normalize_remote_type,
    _normalize_time_posted,
)
from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL
from linkedin_web_scraper.config.options import EnrichmentProvider, RemoteType, TimePosted


class JobScraperConfigFactory:
    """Factory helpers for constructing normalized scraper config objects."""

    @staticmethod
    def create(
        position: str,
        location: str,
        enrichment_provider: str | EnrichmentProvider = EnrichmentProvider.NONE,
        enrichment_model: str = DEFAULT_OPENAI_MODEL,
        time_posted: str | TimePosted = TimePosted.DAY,
        remote: str | RemoteType = RemoteType.ALL,
        *,
        enrichment_required: bool = False,
        distance: int = 10,
        advanced_config: JobScraperAdvancedConfig | None = None,
    ) -> JobScraperConfig:
        """Build a normalized scraper configuration from user-facing inputs."""
        return JobScraperConfig(
            position=position,
            location=location,
            enrichment_provider=_normalize_enrichment_provider(enrichment_provider),
            enrichment_required=enrichment_required,
            enrichment_model=enrichment_model,
            time_posted=_normalize_time_posted(time_posted),
            remote=_normalize_remote_type(remote),
            distance=distance,
            advanced_config=advanced_config,
        )
