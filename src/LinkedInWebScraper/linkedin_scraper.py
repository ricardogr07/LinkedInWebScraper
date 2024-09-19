import pandas as pd

from LinkedInWebScraper.job_scraper import JobScraper
from LinkedInWebScraper.job_scraper_config import JobScraperConfig
from LinkedInWebScraper.job_data_cleaner import JobDataCleaner
from LinkedInWebScraper.job_title_classifier import JobTitleClassifier
from LinkedInWebScraper.job_description_processor import JobDescriptionProcessor
from OpenAIHandler.openai_handler import OpenAIHandler
from Utils.logger import Logger

from Utils.constants import LOCATION_MAPPING, DATA_SCIENCE_KEYWORDS, TECH_STACK_CATEGORIES

class LinkedInJobScraper:
    def __init__(self, logger: Logger, config: JobScraperConfig):
        self.config = config
        self.logger = logger

        self.job_scraper = JobScraper(config=self.config, logger=self.logger)
        self.job_data_cleaner = JobDataCleaner(self.logger)

        self.initialize_advanced_config()
 
        self.job_title_classifier = JobTitleClassifier(self.logger, self.config.position, self.KEYWORDS)

        if self.config.openai_enabled:
            openai_handler = OpenAIHandler(self.logger)
            self.description_processor = JobDescriptionProcessor(openai_handler, self.logger)

    def initialize_advanced_config(self):
        """
        Initializes advanced configuration attributes (LOCATION_MAPPING, KEYWORDS, SKILLS_CATEGORIES)
        from the advanced configuration if provided.
        """
        # Set defaults to None
        self.LOCATION_MAPPING = None
        self.KEYWORDS = None
        self.SKILLS_CATEGORIES = None

        # Check if advanced_config is provided and set attributes if available
        if self.config.advanced_config:
            self.LOCATION_MAPPING = getattr(self.config.advanced_config, 'LOCATION_MAPPING', None)
            self.KEYWORDS = getattr(self.config.advanced_config, 'KEYWORDS', None)
            self.SKILLS_CATEGORIES = getattr(self.config.advanced_config, 'SKILLS_CATEGORIES', None)

    def run(self) -> pd.DataFrame:
        """Main function to run the LinkedIn job scraping process."""
        try:
            self.logger.log.info(f'Running scraping job for {self.config.remote} {self.config.position} positions.')
            scraped_jobs = self.scrape_jobs()

            if scraped_jobs.empty:
                self.logger.log.warning(f"No jobs found for {self.config.remote} {self.config.position}.")
                return pd.DataFrame()

            cleaned_jobs = self.clean_jobs(scraped_jobs)

            if self.KEYWORDS != None:
                classified_jobs = self.classify_jobs(cleaned_jobs)
            else:
                classified_jobs = cleaned_jobs

            if classified_jobs.empty:
                self.logger.log.warning(f"No jobs remain after title classification.")
                return pd.DataFrame()
            
            jobs_with_details = self.fetch_job_details(classified_jobs)

            cleaned_jobs_with_details = self.clean_job_details(jobs_with_details)

            if self.config.openai_enabled:      
                enriched_jobs = self.enrich_jobs_with_descriptions(cleaned_jobs_with_details)
                final_jobs = self.final_processing(enriched_jobs)
                return final_jobs
            else:
                self.logger.log.info(f'The OpenAI Enabled feature is  {self.config.openai_enabled}. Returning jobs with details only. ')
                return jobs_with_details

        except Exception as e:
            self.logger.log.exception(f"An error occurred during the scraping process: {e}")
            return pd.DataFrame()

    def scrape_jobs(self) -> pd.DataFrame:
        """Scrape jobs from LinkedIn using JobScraper."""
        try:
            scraped_jobs = self.job_scraper.scrape_jobs()
            if scraped_jobs.empty:
                self.logger.log.warning(f"No jobs found for {self.config.position} positions.")
            return scraped_jobs
        except Exception as e:
            self.logger.log.exception(f"Failed to scrape jobs: {e}")
            return pd.DataFrame()

    def clean_jobs(self, scraped_jobs: pd.DataFrame) -> pd.DataFrame:
        """Clean the scraped job data using JobDataCleaner."""
        try:
            cleaned_jobs = self.job_data_cleaner.clean_jobs_dataframe(scraped_jobs, self.LOCATION_MAPPING)
            if cleaned_jobs.empty:
                self.logger.log.warning(f"No jobs remain after cleaning for {self.config.remote} {self.config.position}.")
            return cleaned_jobs
        except Exception as e:
            self.logger.log.exception(f"Failed to clean jobs data: {e}")
            return pd.DataFrame()

    def classify_jobs(self, cleaned_jobs: pd.DataFrame) -> pd.DataFrame:
        """Classify job titles using JobTitleClassifier."""
        try:  
            classified_jobs = self.job_title_classifier.classify_title(cleaned_jobs)
            if classified_jobs.empty:
                self.logger.log.warning(f"No jobs remain after classification.")
            return classified_jobs
        except Exception as e:
            self.logger.log.exception(f"Failed to classify job titles: {e}")
            return pd.DataFrame()

    def fetch_job_details(self, classified_jobs: pd.DataFrame) -> pd.DataFrame:
        """Fetch job details using the JobScraper."""
        try:
            jobs_with_details = self.job_scraper.fetch_job_details(classified_jobs)
            return jobs_with_details
        except Exception as e:
            self.logger.log.exception(f"Failed to fetch job details: {e}")
            return pd.DataFrame()

    def clean_job_details(self,jobs_with_details:pd.DataFrame ) ->pd.DataFrame:
        try:
            cleaned_jobs_with_details = self.job_data_cleaner.clean_extracted_job_data(jobs_with_details)
            return cleaned_jobs_with_details
        except Exception as e:
            self.logger.log.exception(f"Failed to clean extracted job data: {e}")
            return pd.DataFrame()

    def enrich_jobs_with_descriptions(self, cleaned_jobs_with_details: pd.DataFrame) -> pd.DataFrame:
        """Enrich job data by processing job descriptions with OpenAIHandler."""
        try:
            enriched_jobs = self.description_processor.process_job_descriptions(cleaned_jobs_with_details)
            return enriched_jobs
        except Exception as e:
            self.logger.log.exception(f"Failed to enrich job descriptions: {e}")
            return pd.DataFrame()

    def final_processing(self, enriched_jobs: pd.DataFrame) -> pd.DataFrame:
        """Perform final processing on the enriched job data."""
        try:
            final_jobs = self.job_data_cleaner.process_enriched_job_data(enriched_jobs,self.SKILLS_CATEGORIES)
            return final_jobs
        except Exception as e:
            self.logger.log.exception(f"Failed during final job data processing: {e}")
            return pd.DataFrame()
