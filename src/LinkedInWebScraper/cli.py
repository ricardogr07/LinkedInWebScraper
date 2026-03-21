from __future__ import annotations

import pandas as pd

from LinkedInWebScraper.job_scraper_config import JobScraperConfig
from LinkedInWebScraper.job_scraper_config_factory import JobScraperConfigFactory
from LinkedInWebScraper.linkedin_scraper import LinkedInJobScraper
from Utils.file_manager import FileManager
from Utils.logger import Logger


def main() -> int:
    """Run the current daily scraper workflow as a temporary console entrypoint."""
    cities = ["Monterrey", "Guadalajara", "Mexico City"]
    logger = Logger("main.log")

    logger.log.info("Initializing web scraping for LinkedIn Jobs for the configured cities.")

    for city in cities:
        city_filename = city.replace(" ", "_")
        file_name = f"LinkedIn_Jobs_Data_Scientist_{city_filename}.csv"
        scraper_results = {}

        for remote in ["REMOTE", "HYBRID", "ON-SITE"]:
            config = JobScraperConfigFactory.create(
                position="Data Scientist",
                location=city,
                openai_enabled=False,
                time_posted="DAY",
                remote=remote,
            )
            scraper = LinkedInJobScraper(logger=logger, config=config)
            scraper_results[remote] = scraper.run()

        combined_city = pd.concat(
            [
                scraper_results.get("REMOTE", pd.DataFrame()),
                scraper_results.get("HYBRID", pd.DataFrame()),
                scraper_results.get("ON-SITE", pd.DataFrame()),
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
    logger.log.info(
        "Saved the final concatenated jobs data to LinkedIn_Jobs_Data_Scientist_Mexico.csv."
    )
    return 0
