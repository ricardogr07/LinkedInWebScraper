from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.interfaces.cli.main import main

warn_legacy_namespace("LinkedInWebScraper.cli")

__all__ = ["main"]