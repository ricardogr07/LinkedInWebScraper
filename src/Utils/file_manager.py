import os
import pandas as pd
from Utils.logger import Logger
from LinkedInWebScraper.job_scraper_config import JobScraperConfig
from datetime import datetime


class FileManager:
    def __init__(self, logger: Logger, config : JobScraperConfig):
        self.logger = logger
        self.position = config.position
        self.location = config.location
        self.time_posted = config.time_posted
        self.remote = config.remote

    def save_jobs_to_csv(self, df, file_name=None, append=True):
        """Save or append jobs to CSV file."""
        if file_name is None:
            file_name = self.generate_file_name()

        if append and os.path.exists(file_name):
            self.append_jobs_to_csv(df, file_name)
        else:
            self.save_new_jobs_to_csv(df, file_name)

    def generate_file_name(self):
        """Generate a file name based on the position, location, and date."""
        date = datetime.now().strftime('%Y-%m-%d')
        position_filename = self.position.replace(" ", "_")
        location_filename = self.location.replace(" ", "_")
        file_name = f'LinkedIn_Jobs_{position_filename}_{location_filename}'

        if self.time_posted != 'ALL':
            file_name += f'_LAST_{self.time_posted}'
        if self.remote != 'ALL':
            file_name += f'_{self.remote}'

        file_name += f'_{date}.csv'
        return file_name

    def append_jobs_to_csv(self, df, file_name):
        """Append new jobs to an existing CSV file."""
        existing_df = pd.read_csv(file_name)
        existing_df = self.clean_job_ids(existing_df)
        df = self.clean_job_ids(df)

        df_filtered = df[~df['JobID'].isin(existing_df['JobID'])]
        new_entries_count = len(df_filtered)

        if new_entries_count > 0:
            combined_df = pd.concat([existing_df, df_filtered], ignore_index=True)
            combined_df.to_csv(file_name, index=False)
            self.logger.log.info(f"Appended {new_entries_count} new jobs to {file_name}.")
        else:
            self.logger.log.info(f"No new jobs to append to {file_name}.")

    def save_new_jobs_to_csv(self, df, file_name):
        """Save new jobs to a CSV file."""
        df.to_csv(file_name, index=False)
        self.logger.log.info(f"Saved jobs to {file_name}.")

    def clean_job_ids(self, df):
        """Clean job IDs by stripping whitespace and converting to string."""
        df['JobID'] = df['JobID'].astype(str).str.strip()
        return df

