from __future__ import annotations

import pandas as pd

from linkedin_web_scraper.application.linkedin_job_scraper import LinkedInJobScraper
from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
from linkedin_web_scraper.config.job_scraper_config_factory import JobScraperConfigFactory
from linkedin_web_scraper.config.options import RemoteType, TimePosted
from linkedin_web_scraper.infra.logging import configure_logging, get_logger
from linkedin_web_scraper.infra.storage.file_manager import FileManager


def main() -> int:
    """Run the current daily scraper workflow as a temporary console entrypoint."""
    cities = ["Monterrey", "Guadalajara", "Mexico City"]
    configure_logging(filename="main.log")
    logger = get_logger(__name__)

    logger.info("Initializing web scraping for LinkedIn Jobs for the configured cities.")

    for city in cities:
        city_filename = city.replace(" ", "_")
        file_name = f"LinkedIn_Jobs_Data_Scientist_{city_filename}.csv"
        scraper_results = {}

        for remote in [RemoteType.REMOTE, RemoteType.HYBRID, RemoteType.ON_SITE]:
            config = JobScraperConfigFactory.create(
                position="Data Scientist",
                location=city,
                openai_enabled=False,
                time_posted=TimePosted.DAY,
                remote=remote,
            )
            scraper = LinkedInJobScraper(logger=logger, config=config)
            scraper_results[str(remote)] = scraper.run()

        combined_city = pd.concat(
            [
                scraper_results.get(str(RemoteType.REMOTE), pd.DataFrame()),
                scraper_results.get(str(RemoteType.HYBRID), pd.DataFrame()),
                scraper_results.get(str(RemoteType.ON_SITE), pd.DataFrame()),
            ],
            ignore_index=True,
        )
        file_manager = FileManager(logger, JobScraperConfig("Data Scientist", city, remote="ALL"))
        file_manager.save_jobs_to_csv(df=combined_city, file_name=file_name, append=True)

    frames = [
        pd.read_csv("LinkedIn_Jobs_Data_Scientist_Monterrey.csv"),
        pd.read_csv("LinkedIn_Jobs_Data_Scientist_Guadalajara.csv"),
        pd.read_csv("LinkedIn_Jobs_Data_Scientist_Mexico_City.csv"),
    ]
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv("LinkedIn_Jobs_Data_Scientist_Mexico.csv", index=False)
    logger.info("Saved the final concatenated jobs data to LinkedIn_Jobs_Data_Scientist_Mexico.csv.")
    return 0
