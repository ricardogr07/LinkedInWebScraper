"""Helpers for applying structured OpenAI enrichment to job dataframes."""

from __future__ import annotations

import json
import logging
from typing import Any, cast

import pandas as pd

from linkedin_web_scraper.infra.logging import Logger, resolve_logger
from linkedin_web_scraper.infra.openai.models import NOT_AVAILABLE, JobDescriptionEnricher

ENRICHMENT_COLUMN_DEFAULTS: dict[str, object] = {
    "ShortDescription": NOT_AVAILABLE,
    "TechStack": NOT_AVAILABLE,
    "YoE": NOT_AVAILABLE,
    "MinLevelStudies": NOT_AVAILABLE,
    "English": NOT_AVAILABLE,
    "OpenAIModel": NOT_AVAILABLE,
    "OpenAIResponseId": NOT_AVAILABLE,
    "OpenAIRawPayload": "",
}


class JobDescriptionProcessor:
    """Use a structured enricher to enrich scraped job descriptions."""

    def __init__(
        self,
        openai_handler: JobDescriptionEnricher,
        logger: logging.Logger | Logger | None = None,
    ):
        self.openai_handler = openai_handler
        self.logger = resolve_logger(logger, name=__name__)

    def process_job_descriptions(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Process job descriptions and append parsed fields without failing the scrape."""
        self.logger.info("Processing %s job descriptions using OpenAI enrichment.", len(df_jobs))
        enriched_jobs = df_jobs.copy()
        self._ensure_enrichment_columns(enriched_jobs)
        mutable_jobs = cast(Any, enriched_jobs)

        if "Description" not in enriched_jobs.columns:
            self.logger.warning("Description column is missing. Skipping OpenAI enrichment.")
            return enriched_jobs

        for index, row in enriched_jobs.iterrows():
            description = str(row.get("Description", "")).strip()
            if not description:
                self.logger.warning(
                    "Job description missing for JobID %s. Leaving enrichment columns at defaults.",
                    row.get("JobID", NOT_AVAILABLE),
                )
                continue

            try:
                enrichment = self.openai_handler.extract_job_description(description)
            except Exception:
                self.logger.exception(
                    "Failed to enrich job description for JobID %s. Leaving row unchanged.",
                    row.get("JobID", NOT_AVAILABLE),
                )
                continue

            mutable_jobs.loc[index, "ShortDescription"] = enrichment.short_description
            mutable_jobs.loc[index, "TechStack"] = enrichment.tech_stack_text
            mutable_jobs.loc[index, "YoE"] = enrichment.years_of_experience
            mutable_jobs.loc[index, "MinLevelStudies"] = enrichment.minimum_level_of_studies
            mutable_jobs.loc[index, "English"] = enrichment.english_requirement_text
            mutable_jobs.loc[index, "OpenAIModel"] = enrichment.model or NOT_AVAILABLE
            mutable_jobs.loc[index, "OpenAIResponseId"] = enrichment.response_id or NOT_AVAILABLE
            mutable_jobs.loc[index, "OpenAIRawPayload"] = json.dumps(
                enrichment.raw_payload, ensure_ascii=True, sort_keys=True
            )

        self.logger.info("Finished processing job descriptions.")
        return enriched_jobs

    @staticmethod
    def _ensure_enrichment_columns(df_jobs: pd.DataFrame) -> None:
        for column, default_value in ENRICHMENT_COLUMN_DEFAULTS.items():
            if column in df_jobs.columns:
                df_jobs[column] = df_jobs[column].astype(object)
                continue

            df_jobs[column] = pd.Series(
                [default_value] * len(df_jobs),
                index=df_jobs.index,
                dtype=object,
            )


__all__ = ["ENRICHMENT_COLUMN_DEFAULTS", "JobDescriptionProcessor"]
