from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.domain.job_title_classifier import JobTitleClassifier

warn_legacy_namespace("LinkedInWebScraper.job_title_classifier")

__all__ = ["JobTitleClassifier"]