from __future__ import annotations

from linkedin_web_scraper.config.job_scraper_advanced_config import JobScraperAdvancedConfig
from linkedin_web_scraper.config.job_scraper_config import (
    JobScraperConfig,
    _normalize_remote_type,
    _normalize_time_posted,
)
from linkedin_web_scraper.config.options import RemoteType, TimePosted


class JobScraperConfigFactory:
    """Factory helpers for constructing normalized scraper config objects."""

    @staticmethod
    def create(
        position: str,
        location: str,
        openai_enabled: bool = False,
        time_posted: str | TimePosted = TimePosted.DAY,
        remote: str | RemoteType = RemoteType.ALL,
        *,
        distance: int = 10,
        advanced_config: JobScraperAdvancedConfig | None = None,
    ) -> JobScraperConfig:
        """Build a normalized scraper configuration from user-facing inputs."""
        return JobScraperConfig(
            position=position,
            location=location,
            openai_enabled=openai_enabled,
            time_posted=_normalize_time_posted(time_posted),
            remote=_normalize_remote_type(remote),
            distance=distance,
            advanced_config=advanced_config,
        )
