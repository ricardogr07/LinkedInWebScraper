from __future__ import annotations

import re

from linkedin_web_scraper.infra.logging import resolve_logger


class JobTitleClassifier:
    """Filter scraped jobs to titles related to the requested position."""

    def __init__(self, logger=None, position: str = "", keywords: list[str] | None = None):
        self.logger = resolve_logger(logger, name=__name__)
        self.position = position
        self.keywords = [keyword.lower() for keyword in keywords] if keywords is not None else []

        if self.keywords:
            self.logger.info(
                "Initialized JobTitleClassifier with keywords: %s for %s",
                self.keywords,
                self.position,
            )
        else:
            self.logger.info("No keywords were given. Running without classifying job titles.")

    def classify_title(self, df_jobs):
        """Classify job titles based on keywords and filter out unrelated jobs."""
        if not self.keywords:
            return df_jobs

        if "Title" not in df_jobs.columns:
            self.logger.error(
                "The DataFrame does not contain a 'Title' column. No action will be performed."
            )
            return df_jobs

        self.logger.info(
            "Starting classification of %s %s job titles.", len(df_jobs), self.position
        )
        df_jobs["DS_Related"] = df_jobs["Title"].apply(self._classify_single_title)

        related_jobs_count = df_jobs["DS_Related"].sum()
        self.logger.info(
            "Classified %s jobs as related to %s.", related_jobs_count, self.position
        )

        df_jobs = df_jobs.loc[df_jobs["DS_Related"] == 1].copy()
        df_jobs.drop(columns=["DS_Related"], inplace=True)

        self.logger.info(
            "Returning DataFrame with %s %s related jobs.", len(df_jobs), self.position
        )
        return df_jobs

    def _classify_single_title(self, title: str) -> int:
        """Classify a single job title by checking if it contains any configured keywords."""
        title_lower = title.lower()

        for keyword in self.keywords:
            if re.search(rf"\b{keyword}\b", title_lower):
                self.logger.debug("Title '%s' matches keyword '%s'", title, keyword)
                return 1

        self.logger.debug("Title '%s' does not match any keywords.", title)
        return 0
