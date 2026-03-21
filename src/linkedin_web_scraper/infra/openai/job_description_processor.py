from __future__ import annotations

import logging

import pandas as pd

from linkedin_web_scraper.infra.logging import Logger, resolve_logger
from linkedin_web_scraper.infra.openai.openai_handler import OpenAIHandler


class JobDescriptionProcessor:
    """Use an OpenAI handler to enrich scraped job descriptions."""

    def __init__(
        self,
        openai_handler: OpenAIHandler,
        logger: logging.Logger | Logger | None = None,
    ):
        self.openai_handler = openai_handler
        self.logger = resolve_logger(logger, name=__name__)

    def process_job_descriptions(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Process job descriptions using the OpenAI API and append parsed fields."""
        self.logger.info("Processing %s job descriptions using OpenAI API.", len(df_jobs))

        for index, row in df_jobs.iterrows():
            messages = self.openai_handler.create_messages(row["Description"])
            response = self.openai_handler.generate_chat_completion(messages)

            df_jobs.at[index, "ShortDescription"] = response.get("Description", "N/A")
            df_jobs.at[index, "TechStack"] = ", ".join(response.get("TechStack", []))
            df_jobs.at[index, "YoE"] = response.get("YoE", "N/A")
            df_jobs.at[index, "MinLevelStudies"] = response.get("MinLevelStudies", "N/A")
            df_jobs.at[index, "English"] = response.get("English", "N/A")

        self.logger.info("Finished processing job descriptions.")
        return df_jobs
