from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.infra.logging import Logger

warn_legacy_namespace("Utils.logger")

__all__ = ["Logger"]