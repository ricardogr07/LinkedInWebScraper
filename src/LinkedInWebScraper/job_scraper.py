from bs4 import BeautifulSoup
import pandas as pd
import math

from Utils.logger import Logger
from LinkedInWebScraper.job_scraper_config import JobScraperConfig
from LinkedInWebScraper.utils import fetch_until_success
from Utils.constants import TIME_POSTED_OPTION, REMOTE_OPTION


class JobScraper:
    def __init__(self, config: JobScraperConfig, logger:Logger):
        self.config = config
        self.logger = logger
        self.jobs = []

    def scrape_jobs(self) -> pd.DataFrame:
        """Scrape jobs from LinkedIn across multiple pages."""
        try:
            self.logger.log.info(f"Starting job scraping with config: {self.config}")
            total_jobs = self.fetch_total_jobs()
            if total_jobs == 0:
                self.logger.log.warning("No jobs found for the given search criteria.")
                return pd.DataFrame()

            total_pages = math.ceil(total_jobs / 10)
            self.logger.log.info(f"Found {total_jobs} jobs. Scraping {total_pages} pages.")

            for i in range(0, total_jobs, 10):
                current_page = i // 10 + 1
                target_url = self.generate_paginated_url(i)
                response = fetch_until_success(target_url, self.logger)

                if response:
                    self.logger.log.info(f"Parsing data for page {current_page}/{total_pages}.")
                    self.parse_job_data(response.content)
                else:
                    self.logger.log.error(f"Failed to fetch data for page {current_page}.")

            df = pd.DataFrame(self.jobs)
            df = df[df['Url'] != 'N/A']


            self.logger.log.info(f"Scraped {df.shape[0]} jobs for the {self.config.remote} positions.")

            return df

        except Exception as e:
            self.logger.log.error(f"An error occurred during scraping: {e}")

    def fetch_total_jobs(self):
        """Fetch and return the total number of jobs available for the search criteria."""
        try:
            url = self.generate_main_url()
            response = fetch_until_success(url, self.logger)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_count_element = soup.find('span', {'class': 'results-context-header__job-count'})
                total_jobs = int(job_count_element.text.strip().replace(',', '')) if job_count_element else 0
                return total_jobs
            else:
                self.logger.log.error("Failed to fetch the total number of jobs.")
                return 0
        except Exception as e:
            self.logger.log.error(f"Error fetching total jobs: {e}")
            return 0

    def generate_main_url(self):
        """Generate the main LinkedIn job search URL with the specified filters."""
        base_url = 'https://www.linkedin.com/jobs/search/'
        url_friendly_position = self.config.position.replace(" ", "%20")
        query_params = f'?keywords={url_friendly_position}&location={self.config.location}'

        if self.config.distance:
            query_params += f'&distance={self.config.distance}'
        if self.config.time_posted:
            time_posted_value = TIME_POSTED_OPTION.get(self.config.time_posted, '')
            query_params += f'&f_TPR={time_posted_value}'
        if self.config.remote:
            remote_value = REMOTE_OPTION.get(self.config.remote, '')
            query_params += f'&f_WT={remote_value}'

        return base_url + query_params

    def generate_paginated_url(self, start):
        """Generate the paginated URL for fetching jobs from LinkedIn."""
        return f"{self.generate_main_url()}&start={start}"

    def parse_job_data(self, html_content):
        """Parse the job data from the HTML content and add it to the jobs list."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            job_listings = soup.find_all('li')

            for job in job_listings:
                try:
                    job_info = self.extract_job_info(job)
                    if job_info:
                        self.jobs.append(job_info)
                except Exception as e:
                    self.logger.log.error(f"Error processing job listing: {e}")
                    continue
        except Exception as e:
            self.logger.log.error(f"Error parsing job data: {e}")

    def extract_job_info(self, job):
        """Extract job information from a single job listing."""
        try:
            info = job.find('div', class_="base-search-card__info")
            title = info.find('h3', class_="base-search-card__title").text.strip() if info else 'N/A'
            company = info.find('h4', class_="base-search-card__subtitle").text.strip() if info else 'N/A'

            metadata = job.find('div', class_="base-search-card__metadata")
            location_element = metadata.find('span', class_="job-search-card__location") if metadata else None
            location_job = location_element.text.strip() if location_element else 'N/A'

            joburl_element = job.find('a', class_="base-card__full-link")
            joburl = joburl_element['href'] if joburl_element else 'N/A'

            return {
                'Location': location_job,
                'Title': title,
                'Company': company,
                'Url': joburl,
                'Remote': self.config.remote
            }
        except Exception as e:
            self.logger.log.error(f"Error extracting job info: {e}")
            return None

    def fetch_job_details(self, df_jobs:pd.DataFrame):
        """Fetch detailed job information for each job posting."""
        df_jobs.reset_index(drop=True, inplace=True)
        self.logger.log.info(f"Fetching job description for {df_jobs.shape[0]} postings")
        extracted_data = []

        for i in range(df_jobs.shape[0]):
            jobid = str(df_jobs['JobID'][i])
            target_url = self.get_jobid_information(jobid)
            response = fetch_until_success(target_url, self.logger)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize values as 'N/A'
            seniority_level = 'N/A'
            employment_type = 'N/A'
            job_function = 'N/A'
            industries = 'N/A'
            
            # Find job criteria list
            criteria_list = soup.find('ul', class_='description__job-criteria-list')
            if criteria_list:
                criteria_items = criteria_list.find_all('li', class_='description__job-criteria-item')
                for item in criteria_items:
                    if 'Seniority level' in item.get_text():
                        seniority_level = item.find('span', class_='description__job-criteria-text').get_text(strip=True)
                    elif 'Employment type' in item.get_text():
                        employment_type = item.find('span', class_='description__job-criteria-text').get_text(strip=True)
                    elif 'Job function' in item.get_text():
                        job_function = item.find('span', class_='description__job-criteria-text').get_text(strip=True)
                    elif 'Industries' in item.get_text():
                        industries = item.find('span', class_='description__job-criteria-text').get_text(strip=True)
            
            # Extract additional job information
            num_applicants_tag = soup.find('figcaption', class_='num-applicants__caption') or \
                                 soup.find('span', class_='num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet')
            num_applicants = num_applicants_tag.get_text(strip=True) if num_applicants_tag else 'N/A'
            
            posted_time = soup.find('span', class_='posted-time-ago__text')
            posted_time = posted_time.get_text(strip=True) if posted_time else 'N/A'
            
            description_tag = soup.find('div', class_='show-more-less-html__markup')
            description = description_tag.get_text(separator=' ', strip=True) if description_tag else 'N/A'
            
            # Append the extracted data
            extracted_data.append({
                'SeniorityLevel': seniority_level,
                'EmploymentType': employment_type,
                'JobFunction': job_function,
                'Industries': industries,
                'PostedTime': posted_time,
                'NumApplicants': num_applicants,
                'Description': description
            })
        
        # Convert the extracted data into a DataFrame
        self.logger.log.info(f"Finished fetching job descriptions for {len(extracted_data)} jobs.")
        extracted_df = pd.DataFrame(extracted_data)

        # Merge the job details with the original DataFrame
        return pd.concat([df_jobs, extracted_df], axis=1)

    def get_jobid_information(self, jobid):
        """Generate the URL to fetch detailed job posting data based on job ID."""
        base_url = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/'
        return base_url + jobid
 