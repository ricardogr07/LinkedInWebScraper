"""Storage-layer exports for filesystem and SQLite-backed persistence helpers."""

from linkedin_web_scraper.infra.storage.file_manager import FileManager
from linkedin_web_scraper.infra.storage.sqlite import SQLiteScrapeStorage

__all__ = ["FileManager", "SQLiteScrapeStorage"]
