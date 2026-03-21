from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.infra.http.utils import fetch_until_success, get_random_header

warn_legacy_namespace("LinkedInWebScraper.utils")

__all__ = ["fetch_until_success", "get_random_header"]