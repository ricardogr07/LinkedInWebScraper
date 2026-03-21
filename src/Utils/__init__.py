from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.config.constants import (
    DATA_SCIENCE_KEYWORDS,
    LOCATION_MAPPING,
    REMOTE_OPTION,
    TECH_STACK_CATEGORIES,
    TIME_POSTED_OPTION,
    USER_AGENT_HEADERS,
)
from linkedin_web_scraper.infra.logging import Logger
from linkedin_web_scraper.infra.storage.file_manager import FileManager

warn_legacy_namespace("Utils")

__all__ = [
    "TIME_POSTED_OPTION",
    "REMOTE_OPTION",
    "USER_AGENT_HEADERS",
    "LOCATION_MAPPING",
    "DATA_SCIENCE_KEYWORDS",
    "TECH_STACK_CATEGORIES",
    "FileManager",
    "Logger",
]