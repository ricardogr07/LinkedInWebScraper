from __future__ import annotations

from datetime import datetime

from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.infra.storage import file_manager as canonical_file_manager

warn_legacy_namespace("Utils.file_manager")

os = canonical_file_manager.os
pd = canonical_file_manager.pd


class FileManager(canonical_file_manager.FileManager):
    def generate_file_name(self):
        """Generate a file name based on the position, location, and date."""
        date = datetime.now().strftime("%Y-%m-%d")
        position_filename = self.position.replace(" ", "_")
        location_filename = self.location.replace(" ", "_")
        file_name = f"LinkedIn_Jobs_{position_filename}_{location_filename}"

        if self.time_posted != "ALL":
            file_name += f"_LAST_{self.time_posted}"
        if self.remote != "ALL":
            file_name += f"_{self.remote}"

        file_name += f"_{date}.csv"
        return file_name


__all__ = ["FileManager", "datetime", "os", "pd"]