"""Application-level runtime helpers for CLI and scheduled executions."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from linkedin_web_scraper.application.daily_scrape_service import (
    DailyScrapeService,
    resolve_output_path,
)
from linkedin_web_scraper.config.runtime import RuntimeConfig
from linkedin_web_scraper.config.storage import build_sqlite_storage_url
from linkedin_web_scraper.infra.logging import Logger, resolve_logger
from linkedin_web_scraper.infra.storage.sqlite import SQLiteScrapeStorage


class RuntimeRunner:
    """Execute runtime-configured scrape and export workflows."""

    def __init__(
        self,
        logger: logging.Logger | Logger | None = None,
        *,
        daily_service_cls=DailyScrapeService,
        storage_cls=SQLiteScrapeStorage,
    ):
        self.logger = resolve_logger(logger, name=__name__)
        self.daily_service_cls = daily_service_cls
        self.storage_cls = storage_cls

    def build_storage_url(self, runtime_config: RuntimeConfig) -> str:
        """Resolve the SQLite storage URL from runtime settings."""
        return runtime_config.storage.url or build_sqlite_storage_url(
            runtime_config.storage.file_name,
            state_dir=runtime_config.storage.state_dir,
        )

    def describe_once(self, runtime_config: RuntimeConfig) -> dict[str, Any]:
        """Describe the resolved single-location scrape plan."""
        config = runtime_config.scrape_once
        output_file_name = config.file_name or "<generated>"
        return {
            "command": "scrape once",
            "position": config.position,
            "location": config.location,
            "remote_types": [str(remote_type) for remote_type in config.remote_types],
            "time_posted": str(config.time_posted),
            "openai_enabled": config.openai_enabled,
            "openai_model": config.openai_model,
            "output_path": resolve_output_path(output_file_name, config.output_dir),
            "storage_url": self.build_storage_url(runtime_config),
        }

    def describe_daily(self, runtime_config: RuntimeConfig) -> dict[str, Any]:
        """Describe the resolved daily multi-city scrape plan."""
        config = runtime_config.scrape_daily
        output_file_name = config.combined_file_name or "<generated>"
        return {
            "command": "scrape daily",
            "cities": list(config.cities),
            "position": config.position,
            "time_posted": str(config.time_posted),
            "openai_enabled": config.openai_enabled,
            "openai_model": config.openai_model,
            "output_path": resolve_output_path(output_file_name, config.output_dir),
            "storage_url": self.build_storage_url(runtime_config),
        }

    def describe_export(self, runtime_config: RuntimeConfig) -> dict[str, Any]:
        """Describe the resolved CSV export plan for a persisted scrape run."""
        config = runtime_config.export
        return {
            "command": "export",
            "run_id": config.run_id,
            "output_path": resolve_output_path(config.file_name, config.output_dir),
            "storage_url": self.build_storage_url(runtime_config),
        }

    def run_once(self, runtime_config: RuntimeConfig) -> pd.DataFrame:
        """Run one configured location scrape through the daily service."""
        storage = self._build_storage(runtime_config)
        service = self.daily_service_cls(logger=self.logger, storage=storage)
        config = runtime_config.scrape_once
        try:
            return service.run_for_location(
                position=config.position,
                location=config.location,
                openai_enabled=config.openai_enabled,
                openai_model=config.openai_model,
                time_posted=config.time_posted,
                remote_types=config.remote_types,
                file_name=config.file_name,
                output_dir=config.output_dir,
                append=config.append,
            )
        finally:
            self._dispose_storage(storage)

    def run_daily(self, runtime_config: RuntimeConfig) -> pd.DataFrame:
        """Run the configured daily multi-city scrape workflow."""
        storage = self._build_storage(runtime_config)
        service = self.daily_service_cls(logger=self.logger, storage=storage)
        config = runtime_config.scrape_daily
        try:
            return service.run_daily(
                cities=config.cities,
                position=config.position,
                openai_enabled=config.openai_enabled,
                openai_model=config.openai_model,
                time_posted=config.time_posted,
                output_dir=config.output_dir,
                combined_file_name=config.combined_file_name,
            )
        finally:
            self._dispose_storage(storage)

    def export_run(self, runtime_config: RuntimeConfig) -> str:
        """Export a persisted scrape run to a CSV file."""
        run_id = runtime_config.export.run_id
        if not run_id:
            raise ValueError("A run_id is required to export persisted scrape data.")

        storage = self._build_storage(runtime_config)
        try:
            jobs = storage.load_run_jobs(run_id)
            if jobs.empty:
                raise ValueError(f"No persisted jobs found for run_id {run_id!r}.")

            output_path = resolve_output_path(
                runtime_config.export.file_name,
                runtime_config.export.output_dir,
            )
            jobs.to_csv(output_path, index=False)
            self.logger.info("Exported %s persisted jobs to %s.", len(jobs), output_path)
            return output_path
        finally:
            self._dispose_storage(storage)

    def _build_storage(self, runtime_config: RuntimeConfig) -> SQLiteScrapeStorage:
        return self.storage_cls(
            logger=self.logger,
            storage_url=self.build_storage_url(runtime_config),
        )

    @staticmethod
    def _dispose_storage(storage: object) -> None:
        engine = getattr(storage, "engine", None)
        if engine is not None:
            engine.dispose()


__all__ = ["RuntimeRunner"]
