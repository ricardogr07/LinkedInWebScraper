from LinkedInWebScraper.job_scraper_config import JobScraperConfig

class JobScraperConfigFactory:
    @staticmethod
    def create(position: str, location: str, openai_enabled: bool, time_posted: str, remote: str) -> JobScraperConfig:
        """
        Factory method to create a JobScraperConfig.
        """
        return JobScraperConfig(
            position=position,
            location=location,
            openai_enabled=openai_enabled,
            time_posted=time_posted,
            remote=remote
        )
