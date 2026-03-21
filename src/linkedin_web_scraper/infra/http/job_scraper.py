from __future__ import annotations

import logging
import math

import pandas as pd
import requests
from bs4 import BeautifulSoup

from linkedin_web_scraper.config.constants import REMOTE_OPTION, TIME_POSTED_OPTION
from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
from linkedin_web_scraper.infra.http.utils import fetch_until_success
from linkedin_web_scraper.infra.logging import Logger, resolve_logger


class JobScraper:
    """HTTP-facing scraper for LinkedIn job result pages and detail pages."""

    def __init__(
        self,
        config: JobScraperConfig,
        logger: logging.Logger | Logger | None = None,
        *,
        session: requests.Session | None = None,
        request_timeout: float = 10,
    ):
        self.config = config
        self.logger = resolve_logger(logger, name=__name__)
        self.session = session
        self.request_timeout = request_timeout
        self.jobs: list[dict[str, str]] = []

    def scrape_jobs(self) -> pd.DataFrame:
        """Scrape jobs from LinkedIn across multiple pages."""
        try:
            self.logger.info("Starting job scraping with config: %s", self.config)
            total_jobs = self.fetch_total_jobs()
            if total_jobs == 0:
                self.logger.warning("No jobs found for the given search criteria.")
                return pd.DataFrame()

            total_pages = math.ceil(total_jobs / 10)
            self.logger.info("Found %s jobs. Scraping %s pages.", total_jobs, total_pages)

            for offset in range(0, total_jobs, 10):
                current_page = offset // 10 + 1
                target_url = self.generate_paginated_url(offset)
                response = fetch_until_success(
                    target_url,
                    self.logger,
                    session=self.session,
                    timeout=self.request_timeout,
                )

                if response is None:
                    self.logger.error("Failed to fetch data for page %s.", current_page)
                    continue

                self.logger.info("Parsing data for page %s/%s.", current_page, total_pages)
                self.parse_job_data(response.content)

            df = pd.DataFrame(self.jobs)
            if df.empty:
                return df

            df = df[df["Url"] != "N/A"]
            self.logger.info(
                "Scraped %s jobs for the %s positions.", df.shape[0], self.config.remote
            )
            return df

        except Exception:
            self.logger.exception("An error occurred during scraping.")
            return pd.DataFrame()

    def fetch_total_jobs(self) -> int:
        """Fetch and return the total number of jobs available for the search criteria."""
        try:
            response = fetch_until_success(
                self.generate_main_url(),
                self.logger,
                session=self.session,
                timeout=self.request_timeout,
            )
            if response is None:
                self.logger.error("Failed to fetch the total number of jobs.")
                return 0

            soup = BeautifulSoup(response.text, "html.parser")
            job_count_element = soup.find("span", {"class": "results-context-header__job-count"})
            return int(job_count_element.text.strip().replace(",", "")) if job_count_element else 0
        except Exception:
            self.logger.exception("Error fetching total jobs.")
            return 0

    def generate_main_url(self) -> str:
        """Generate the main LinkedIn job search URL with the specified filters."""
        base_url = "https://www.linkedin.com/jobs/search/"
        url_friendly_position = self.config.position.replace(" ", "%20")
        query_params = f"?keywords={url_friendly_position}&location={self.config.location}"

        if self.config.distance:
            query_params += f"&distance={self.config.distance}"
        if self.config.time_posted:
            query_params += f"&f_TPR={TIME_POSTED_OPTION.get(self.config.time_posted, '')}"
        if self.config.remote:
            query_params += f"&f_WT={REMOTE_OPTION.get(self.config.remote, '')}"

        return base_url + query_params

    def generate_paginated_url(self, start: int) -> str:
        """Generate the paginated URL for fetching jobs from LinkedIn."""
        return f"{self.generate_main_url()}&start={start}"

    def parse_job_data(self, html_content) -> None:
        """Parse the job data from the HTML content and add it to the jobs list."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            job_listings = soup.find_all("li")

            for job in job_listings:
                try:
                    job_info = self.extract_job_info(job)
                    if job_info:
                        self.jobs.append(job_info)
                except Exception:
                    self.logger.exception("Error processing job listing.")
        except Exception:
            self.logger.exception("Error parsing job data.")

    def extract_job_info(self, job) -> dict[str, str] | None:
        """Extract job information from a single job listing."""
        try:
            info = job.find("div", class_="base-search-card__info")
            title = (
                info.find("h3", class_="base-search-card__title").text.strip() if info else "N/A"
            )
            company = (
                info.find("h4", class_="base-search-card__subtitle").text.strip() if info else "N/A"
            )

            metadata = job.find("div", class_="base-search-card__metadata")
            location_element = (
                metadata.find("span", class_="job-search-card__location") if metadata else None
            )
            location_job = location_element.text.strip() if location_element else "N/A"

            joburl_element = job.find("a", class_="base-card__full-link")
            joburl = joburl_element["href"] if joburl_element else "N/A"

            return {
                "Location": location_job,
                "Title": title,
                "Company": company,
                "Url": joburl,
                "Remote": self.config.remote,
            }
        except Exception:
            self.logger.exception("Error extracting job info.")
            return None

    def fetch_job_details(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Fetch detailed job information for each job posting."""
        df_jobs = df_jobs.reset_index(drop=True)
        self.logger.info("Fetching job description for %s postings", df_jobs.shape[0])
        extracted_data = []

        for index in range(df_jobs.shape[0]):
            jobid = str(df_jobs["JobID"][index])
            response = fetch_until_success(
                self.get_jobid_information(jobid),
                self.logger,
                session=self.session,
                timeout=self.request_timeout,
            )
            if response is None:
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            seniority_level = "N/A"
            employment_type = "N/A"
            job_function = "N/A"
            industries = "N/A"

            criteria_list = soup.find("ul", class_="description__job-criteria-list")
            if criteria_list:
                criteria_items = criteria_list.find_all(
                    "li", class_="description__job-criteria-item"
                )
                for item in criteria_items:
                    if "Seniority level" in item.get_text():
                        seniority_level = item.find(
                            "span", class_="description__job-criteria-text"
                        ).get_text(strip=True)
                    elif "Employment type" in item.get_text():
                        employment_type = item.find(
                            "span", class_="description__job-criteria-text"
                        ).get_text(strip=True)
                    elif "Job function" in item.get_text():
                        job_function = item.find(
                            "span", class_="description__job-criteria-text"
                        ).get_text(strip=True)
                    elif "Industries" in item.get_text():
                        industries = item.find(
                            "span", class_="description__job-criteria-text"
                        ).get_text(strip=True)

            num_applicants_tag = soup.find("figcaption", class_="num-applicants__caption") or soup.find(
                "span",
                class_="num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet",
            )
            num_applicants = num_applicants_tag.get_text(strip=True) if num_applicants_tag else "N/A"

            posted_time = soup.find("span", class_="posted-time-ago__text")
            posted_time = posted_time.get_text(strip=True) if posted_time else "N/A"

            description_tag = soup.find("div", class_="show-more-less-html__markup")
            description = (
                description_tag.get_text(separator=" ", strip=True) if description_tag else "N/A"
            )

            extracted_data.append(
                {
                    "SeniorityLevel": seniority_level,
                    "EmploymentType": employment_type,
                    "JobFunction": job_function,
                    "Industries": industries,
                    "PostedTime": posted_time,
                    "NumApplicants": num_applicants,
                    "Description": description,
                }
            )

        self.logger.info("Finished fetching job descriptions for %s jobs.", len(extracted_data))
        extracted_df = pd.DataFrame(extracted_data)
        return pd.concat([df_jobs, extracted_df], axis=1)

    def get_jobid_information(self, jobid: str) -> str:
        """Generate the URL to fetch detailed job posting data based on job ID."""
        return f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{jobid}"
