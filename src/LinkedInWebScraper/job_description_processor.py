from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.infra.openai.job_description_processor import JobDescriptionProcessor

warn_legacy_namespace("LinkedInWebScraper.job_description_processor")

__all__ = ["JobDescriptionProcessor"]