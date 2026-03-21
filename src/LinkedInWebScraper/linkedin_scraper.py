from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.application.linkedin_job_scraper import LinkedInJobScraper

warn_legacy_namespace("LinkedInWebScraper.linkedin_scraper")

__all__ = ["LinkedInJobScraper"]