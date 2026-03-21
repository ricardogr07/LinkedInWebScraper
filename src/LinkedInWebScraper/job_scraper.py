from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.infra.http.job_scraper import JobScraper

warn_legacy_namespace("LinkedInWebScraper.job_scraper")

__all__ = ["JobScraper"]