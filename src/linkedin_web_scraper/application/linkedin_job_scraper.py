"""High-level orchestration for the LinkedIn scraping pipeline."""

from __future__ import annotations

import logging

import pandas as pd

from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
from linkedin_web_scraper.config.options import EnrichmentProvider
from linkedin_web_scraper.domain.job_data_cleaner import JobDataCleaner
from linkedin_web_scraper.domain.job_title_classifier import JobTitleClassifier
from linkedin_web_scraper.infra.anthropic.anthropic_handler import AnthropicHandler
from linkedin_web_scraper.infra.http.job_scraper import JobScraper
from linkedin_web_scraper.infra.logging import Logger, resolve_logger
from linkedin_web_scraper.infra.openai.job_description_processor import JobDescriptionProcessor
from linkedin_web_scraper.infra.openai.models import JobDescriptionEnricher
from linkedin_web_scraper.infra.openai.openai_handler import OpenAIHandler


class LinkedInJobScraper:
    """Coordinate scrape, cleaning, classification, and optional enrichment.

    The class owns the end-to-end library workflow for a single scrape request:
    scrape search results, normalize the dataframe, optionally filter titles,
    fetch detail pages, and optionally enrich descriptions through OpenAI.
    """

    def __init__(
        self,
        logger: logging.Logger | Logger | None,
        config: JobScraperConfig,
        *,
        job_scraper: JobScraper | None = None,
        job_data_cleaner: JobDataCleaner | None = None,
        enricher: JobDescriptionEnricher | None = None,
    ):
        """Build a scraper pipeline with optional dependency overrides."""
        self.config = config
        self.logger = resolve_logger(logger, name=__name__)

        self.job_scraper = job_scraper or JobScraper(config=self.config, logger=self.logger)
        self.job_data_cleaner = job_data_cleaner or JobDataCleaner(self.logger)

        self._initialize_advanced_config()

        self.job_title_classifier = JobTitleClassifier(
            logger=self.logger,
            position=self.config.position,
            keywords=self.keywords,
        )

        self.description_processor: JobDescriptionProcessor | None = None
        if self.config.enrichment_provider is not EnrichmentProvider.NONE:
            self.description_processor = self._create_description_processor(enricher)

    def _initialize_advanced_config(self) -> None:
        """Load optional overrides from the advanced config object."""
        self.location_mapping = None
        self.keywords = None
        self.skills_categories = None

        if self.config.advanced_config is not None:
            self.location_mapping = self.config.advanced_config.LOCATION_MAPPING
            self.keywords = self.config.advanced_config.KEYWORDS
            self.skills_categories = self.config.advanced_config.SKILLS_CATEGORIES

    def _create_description_processor(
        self, enricher: JobDescriptionEnricher | None
    ) -> JobDescriptionProcessor | None:
        try:
            handler = enricher or self._build_enricher()
        except Exception:
            if self.config.enrichment_required:
                self.logger.exception(
                    "Enrichment is required but initialization failed. Failing the run."
                )
                raise
            self.logger.exception(
                "Enrichment requested but initialization failed. Continuing without it."
            )
            return None
        return JobDescriptionProcessor(handler, self.logger)

    def _build_enricher(self) -> JobDescriptionEnricher:
        if self.config.enrichment_provider is EnrichmentProvider.ANTHROPIC:
            return AnthropicHandler(self.logger, model=self.config.enrichment_model)
        return OpenAIHandler(self.logger, model=self.config.enrichment_model)

    def run(self) -> pd.DataFrame:
        """Run the end-to-end scrape pipeline and return the resulting dataframe."""
        try:
            self.logger.info(
                "Running scraping job for %s %s positions.",
                self.config.remote,
                self.config.position,
            )
            scraped_jobs = self.scrape_jobs()

            if scraped_jobs.empty:
                self.logger.warning(
                    "No jobs found for %s %s.", self.config.remote, self.config.position
                )
                return pd.DataFrame()

            cleaned_jobs = self.clean_jobs(scraped_jobs)
            classified_jobs = (
                self.classify_jobs(cleaned_jobs) if self.keywords is not None else cleaned_jobs
            )

            if classified_jobs.empty:
                self.logger.warning("No jobs remain after title classification.")
                return pd.DataFrame()

            jobs_with_details = self.fetch_job_details(classified_jobs)
            cleaned_jobs_with_details = self.clean_job_details(jobs_with_details)

            enrichment_enabled = self.config.enrichment_provider is not EnrichmentProvider.NONE
            if not enrichment_enabled or self.description_processor is None:
                if enrichment_enabled and self.description_processor is None:
                    self.logger.warning(
                        "Enrichment unavailable. Returning jobs with extracted details only."
                    )
                else:
                    self.logger.info(
                        "Enrichment disabled. Returning jobs with extracted details only."
                    )
                return cleaned_jobs_with_details

            enriched_jobs = self.enrich_jobs_with_descriptions(cleaned_jobs_with_details)
            return self.final_processing(enriched_jobs)

        except Exception:
            self.logger.exception("An error occurred during the scraping process.")
            return pd.DataFrame()

    def scrape_jobs(self) -> pd.DataFrame:
        """Scrape jobs from LinkedIn using JobScraper."""
        try:
            scraped_jobs = self.job_scraper.scrape_jobs()
            if scraped_jobs.empty:
                self.logger.warning("No jobs found for %s positions.", self.config.position)
            return scraped_jobs
        except Exception:
            self.logger.exception("Failed to scrape jobs.")
            return pd.DataFrame()

    def clean_jobs(self, scraped_jobs: pd.DataFrame) -> pd.DataFrame:
        """Clean the scraped job data using JobDataCleaner."""
        try:
            cleaned_jobs = self.job_data_cleaner.clean_jobs_dataframe(
                scraped_jobs, self.location_mapping
            )
            if cleaned_jobs.empty:
                self.logger.warning(
                    "No jobs remain after cleaning for %s %s.",
                    self.config.remote,
                    self.config.position,
                )
            return cleaned_jobs
        except Exception:
            self.logger.exception("Failed to clean jobs data.")
            return pd.DataFrame()

    def classify_jobs(self, cleaned_jobs: pd.DataFrame) -> pd.DataFrame:
        """Classify job titles using JobTitleClassifier."""
        try:
            classified_jobs = self.job_title_classifier.classify_title(cleaned_jobs)
            if classified_jobs.empty:
                self.logger.warning("No jobs remain after classification.")
            return classified_jobs
        except Exception:
            self.logger.exception("Failed to classify job titles.")
            return pd.DataFrame()

    def fetch_job_details(self, classified_jobs: pd.DataFrame) -> pd.DataFrame:
        """Fetch job-detail pages for the classified job dataframe."""
        try:
            return self.job_scraper.fetch_job_details(classified_jobs)
        except Exception:
            self.logger.exception("Failed to fetch job details.")
            return pd.DataFrame()

    def clean_job_details(self, jobs_with_details: pd.DataFrame) -> pd.DataFrame:
        """Clean the extracted job details before optional enrichment."""
        try:
            return self.job_data_cleaner.clean_extracted_job_data(jobs_with_details)
        except Exception:
            self.logger.exception("Failed to clean extracted job data.")
            return pd.DataFrame()

    def enrich_jobs_with_descriptions(
        self, cleaned_jobs_with_details: pd.DataFrame
    ) -> pd.DataFrame:
        """Enrich job data by processing job descriptions with OpenAI."""
        if self.description_processor is None:
            return cleaned_jobs_with_details

        try:
            return self.description_processor.process_job_descriptions(cleaned_jobs_with_details)
        except Exception:
            self.logger.exception("Failed to enrich job descriptions. Returning base dataset.")
            return cleaned_jobs_with_details

    def final_processing(self, enriched_jobs: pd.DataFrame) -> pd.DataFrame:
        """Perform final processing on the enriched job data."""
        try:
            return self.job_data_cleaner.process_enriched_job_data(
                enriched_jobs, self.skills_categories
            )
        except Exception:
            self.logger.exception("Failed during final job data processing.")
            return enriched_jobs
