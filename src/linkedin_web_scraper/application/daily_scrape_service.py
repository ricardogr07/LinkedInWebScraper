from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from time import perf_counter

import pandas as pd

from linkedin_web_scraper.application.linkedin_job_scraper import LinkedInJobScraper
from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
from linkedin_web_scraper.config.job_scraper_config_factory import JobScraperConfigFactory
from linkedin_web_scraper.config.options import RemoteType, TimePosted
from linkedin_web_scraper.infra.logging import resolve_logger
from linkedin_web_scraper.infra.storage.file_manager import FileManager

DEFAULT_DAILY_CITIES: tuple[str, ...] = ("Monterrey", "Guadalajara", "Mexico City")
DEFAULT_REMOTE_TYPES: tuple[RemoteType, ...] = (
    RemoteType.REMOTE,
    RemoteType.HYBRID,
    RemoteType.ON_SITE,
)


def format_jobs_output_name(position: str, location: str) -> str:
    """Build the stable CSV name used for daily city outputs."""
    position_filename = position.replace(" ", "_")
    location_filename = location.replace(" ", "_")
    return f"LinkedIn_Jobs_{position_filename}_{location_filename}.csv"


def resolve_output_path(file_name: str | Path, output_dir: str | Path | None = None) -> str:
    """Resolve an output file name relative to an optional output directory."""
    candidate = Path(file_name)

    if candidate.is_absolute() or candidate.parent != Path("."):
        candidate.parent.mkdir(parents=True, exist_ok=True)
        return str(candidate)

    if output_dir is None:
        return str(candidate)

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    return str(target_dir / candidate.name)


class DailyScrapeService:
    """Coordinate city-level daily scrapes and aggregated CSV exports."""

    def __init__(
        self,
        logger=None,
        *,
        scraper_cls=LinkedInJobScraper,
        config_factory=JobScraperConfigFactory,
        file_manager_cls=FileManager,
    ):
        self.logger = resolve_logger(logger, name=__name__)
        self.scraper_cls = scraper_cls
        self.config_factory = config_factory
        self.file_manager_cls = file_manager_cls

    def run_for_location(
        self,
        *,
        position: str = "Data Scientist",
        location: str = "Monterrey",
        openai_enabled: bool = False,
        time_posted: str | TimePosted = TimePosted.DAY,
        remote_types: Sequence[str | RemoteType] = DEFAULT_REMOTE_TYPES,
        file_name: str | None = None,
        output_dir: str | Path | None = None,
        append: bool = True,
    ) -> pd.DataFrame:
        """Run the configured scrape for one location across remote variants."""
        self.logger.info("Starting web scraping for %s in %s.", position, location)

        scraper_results: list[pd.DataFrame] = []
        for remote in remote_types:
            config = self.config_factory.create(
                position=position,
                location=location,
                openai_enabled=openai_enabled,
                time_posted=time_posted,
                remote=remote,
            )
            scraper = self.scraper_cls(logger=self.logger, config=config)
            scraper_results.append(scraper.run())

        combined_jobs = pd.concat(scraper_results, ignore_index=True)
        file_manager_config = JobScraperConfig(
            position=position,
            location=location,
            openai_enabled=openai_enabled,
            time_posted=time_posted,
            remote=RemoteType.ALL,
        )
        file_manager = self.file_manager_cls(self.logger, file_manager_config)

        target_file_name = file_name
        if target_file_name is None and output_dir is not None:
            target_file_name = file_manager.generate_file_name()

        if target_file_name is not None:
            target_path = resolve_output_path(target_file_name, output_dir)
            file_manager.save_jobs_to_csv(df=combined_jobs, file_name=target_path, append=append)
        else:
            file_manager.save_jobs_to_csv(df=combined_jobs, append=append)

        return combined_jobs

    def run_daily(
        self,
        *,
        cities: Sequence[str] = DEFAULT_DAILY_CITIES,
        position: str = "Data Scientist",
        openai_enabled: bool = False,
        time_posted: str | TimePosted = TimePosted.DAY,
        output_dir: str | Path | None = None,
        combined_file_name: str | None = None,
    ) -> pd.DataFrame:
        """Run the default daily scrape across multiple cities and save a combined CSV."""
        overall_start = perf_counter()
        self.logger.info("Initializing web scraping for LinkedIn Jobs for the cities %s.", list(cities))

        city_frames: list[pd.DataFrame] = []
        for city in cities:
            city_start = perf_counter()
            city_file_name = format_jobs_output_name(position, city)
            city_frames.append(
                self.run_for_location(
                    position=position,
                    location=city,
                    openai_enabled=openai_enabled,
                    time_posted=time_posted,
                    file_name=city_file_name,
                    output_dir=output_dir,
                )
            )
            self.logger.info(
                "Finished web scraping for %s. It took %.2f seconds.",
                city,
                perf_counter() - city_start,
            )

        combined_jobs = pd.concat(city_frames, ignore_index=True)
        output_name = combined_file_name or format_jobs_output_name(position, "Mexico")
        combined_output_path = resolve_output_path(output_name, output_dir)
        combined_jobs.to_csv(combined_output_path, index=False)
        self.logger.info("Saved the final concatenated jobs data to %s.", combined_output_path)
        self.logger.info(
            "Web scraping for all cities completed in %.2f seconds.", perf_counter() - overall_start
        )
        return combined_jobs
