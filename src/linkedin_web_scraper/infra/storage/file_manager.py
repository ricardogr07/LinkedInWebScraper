from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from linkedin_web_scraper.infra.logging import resolve_logger
from linkedin_web_scraper.infra.paths import resolve_jobs_output_path

if TYPE_CHECKING:
    from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig


class FileManager:
    """Persist scrape outputs to CSV files."""

    def __init__(
        self,
        logger,
        config: JobScraperConfig,
        *,
        output_dir: str | Path | None = None,
    ):
        self.logger = resolve_logger(logger, name=__name__)
        self.position = config.position
        self.location = config.location
        self.time_posted = config.time_posted
        self.remote = config.remote
        self.output_dir = output_dir

    def save_jobs_to_csv(
        self,
        df: pd.DataFrame,
        file_name: str | None = None,
        append: bool = True,
    ) -> None:
        """Save or append jobs to a CSV file."""
        target_file = resolve_jobs_output_path(
            file_name or self.generate_file_name(), self.output_dir
        )

        if append and os.path.exists(target_file):
            self.append_jobs_to_csv(df, target_file)
        else:
            self.save_new_jobs_to_csv(df, target_file)

    def generate_file_name(self) -> str:
        """Generate a file name based on the position, location, and date."""
        date = datetime.now().strftime("%Y-%m-%d")
        position_filename = self.position.replace(" ", "_")
        location_filename = self.location.replace(" ", "_")
        file_name = f"LinkedIn_Jobs_{position_filename}_{location_filename}"

        if self.time_posted != "ALL":
            file_name += f"_LAST_{self.time_posted}"
        if self.remote != "ALL":
            file_name += f"_{self.remote}"

        return f"{file_name}_{date}.csv"

    def append_jobs_to_csv(self, df: pd.DataFrame, file_name: str) -> None:
        """Append new jobs to an existing CSV file."""
        existing_df = self.clean_job_ids(pd.read_csv(file_name))
        df = self.clean_job_ids(df)

        df_filtered = df[~df["JobID"].isin(existing_df["JobID"])]
        new_entries_count = len(df_filtered)

        if new_entries_count > 0:
            combined_df = pd.concat([existing_df, df_filtered], ignore_index=True)
            combined_df.to_csv(file_name, index=False)
            self.logger.info("Appended %s new jobs to %s.", new_entries_count, file_name)
        else:
            self.logger.info("No new jobs to append to %s.", file_name)

    def save_new_jobs_to_csv(self, df: pd.DataFrame, file_name: str) -> None:
        """Save new jobs to a CSV file."""
        df.to_csv(file_name, index=False)
        self.logger.info("Saved jobs to %s.", file_name)

    def clean_job_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean job IDs by stripping whitespace and converting to strings."""
        df["JobID"] = df["JobID"].astype(str).str.strip()
        return df
