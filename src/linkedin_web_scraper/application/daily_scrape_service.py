from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from time import perf_counter

import pandas as pd

from linkedin_web_scraper.application.linkedin_job_scraper import LinkedInJobScraper
from linkedin_web_scraper.application.storage import ScrapeRunContext, ScrapeStorage
from linkedin_web_scraper.config.job_scraper_config_factory import JobScraperConfigFactory
from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL
from linkedin_web_scraper.config.options import RemoteType, TimePosted
from linkedin_web_scraper.infra.logging import resolve_logger
from linkedin_web_scraper.infra.paths import resolve_jobs_output_path
from linkedin_web_scraper.infra.storage.file_manager import FileManager
from linkedin_web_scraper.infra.storage.sqlite import SQLiteScrapeStorage

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
    """Resolve an output file name under the managed jobs directory by default."""
    return resolve_jobs_output_path(file_name, output_dir)


class DailyScrapeService:
    """Coordinate city-level daily scrapes, persistence, and CSV exports."""

    def __init__(
        self,
        logger=None,
        *,
        scraper_cls=LinkedInJobScraper,
        config_factory=JobScraperConfigFactory,
        file_manager_cls=FileManager,
        storage: ScrapeStorage | None = None,
        storage_cls=SQLiteScrapeStorage,
    ):
        self.logger = resolve_logger(logger, name=__name__)
        self.scraper_cls = scraper_cls
        self.config_factory = config_factory
        self.file_manager_cls = file_manager_cls
        self.storage = storage or storage_cls(logger=self.logger)

    def run_for_location(
        self,
        *,
        position: str = "Data Scientist",
        location: str = "Monterrey",
        openai_enabled: bool = False,
        openai_model: str = DEFAULT_OPENAI_MODEL,
        time_posted: str | TimePosted = TimePosted.DAY,
        remote_types: Sequence[str | RemoteType] = DEFAULT_REMOTE_TYPES,
        file_name: str | None = None,
        output_dir: str | Path | None = None,
        append: bool = True,
    ) -> pd.DataFrame:
        """Run the configured scrape for one location across remote variants."""
        self.logger.info("Starting web scraping for %s in %s.", position, location)

        file_manager_config = self.config_factory.create(
            position=position,
            location=location,
            openai_enabled=openai_enabled,
            openai_model=openai_model,
            time_posted=time_posted,
            remote=RemoteType.ALL,
        )
        file_manager = self.file_manager_cls(
            self.logger,
            file_manager_config,
            output_dir=output_dir,
        )
        target_output_path = resolve_output_path(
            file_name or file_manager.generate_file_name(),
            output_dir,
        )
        run_context = ScrapeRunContext(
            position=position,
            location=location,
            openai_enabled=openai_enabled,
            time_posted=str(time_posted),
            remote_types=tuple(str(remote) for remote in remote_types),
            output_path=target_output_path,
            metadata={"openai_model": openai_model},
        )
        run_id = self.storage.begin_run(run_context)

        try:
            scraper_results: list[pd.DataFrame] = []
            for remote in remote_types:
                config = self.config_factory.create(
                    position=position,
                    location=location,
                    openai_enabled=openai_enabled,
                    openai_model=openai_model,
                    time_posted=time_posted,
                    remote=remote,
                )
                scraper = self.scraper_cls(logger=self.logger, config=config)
                scraper_results.append(scraper.run())

            combined_jobs = pd.concat(scraper_results, ignore_index=True)
            self.storage.store_jobs(run_id, combined_jobs)
            persisted_jobs = self.storage.load_run_jobs(run_id)
            file_manager.save_jobs_to_csv(
                df=persisted_jobs,
                file_name=target_output_path,
                append=append,
            )
            self.storage.finish_run(
                run_id,
                status="completed",
                output_path=target_output_path,
                row_count=len(persisted_jobs),
            )
            return persisted_jobs
        except Exception as error:
            self.storage.finish_run(
                run_id,
                status="failed",
                output_path=target_output_path,
                error_message=str(error),
            )
            raise

    def run_daily(
        self,
        *,
        cities: Sequence[str] = DEFAULT_DAILY_CITIES,
        position: str = "Data Scientist",
        openai_enabled: bool = False,
        openai_model: str = DEFAULT_OPENAI_MODEL,
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
                    openai_model=openai_model,
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
        combined_config = self.config_factory.create(
            position=position,
            location="Mexico",
            openai_enabled=openai_enabled,
            openai_model=openai_model,
            time_posted=time_posted,
            remote=RemoteType.ALL,
        )
        combined_file_manager = self.file_manager_cls(
            self.logger,
            combined_config,
            output_dir=output_dir,
        )
        combined_file_manager.save_jobs_to_csv(
            df=combined_jobs,
            file_name=combined_output_path,
            append=False,
        )
        self.logger.info("Saved the final concatenated jobs data to %s.", combined_output_path)
        self.logger.info(
            "Web scraping for all cities completed in %.2f seconds.", perf_counter() - overall_start
        )
        return combined_jobs
