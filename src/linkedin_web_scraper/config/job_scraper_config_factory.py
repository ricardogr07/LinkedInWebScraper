from __future__ import annotations

from linkedin_web_scraper.config.job_scraper_advanced_config import JobScraperAdvancedConfig
from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
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
        return JobScraperConfig(
            position=position,
            location=location,
            openai_enabled=openai_enabled,
            time_posted=time_posted,
            remote=remote,
            distance=distance,
            advanced_config=advanced_config,
        )
