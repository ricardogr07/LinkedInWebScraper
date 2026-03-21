from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.domain.job_data_cleaner import JobDataCleaner

warn_legacy_namespace("LinkedInWebScraper.job_data_cleaner")

__all__ = ["JobDataCleaner"]