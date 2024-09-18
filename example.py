from LinkedInWebScraper import LinkedInJobScraper, JobScraperConfig, Logger

logger = Logger('example.log')

# Define scraper configuration
config = JobScraperConfig(
    position="Data Scientist",
    location="Monterrey",
    remote="REMOTE"
)

# Initialize the scraper
scraper = LinkedInJobScraper(logger,config)

# Scrape job data
job_data = scraper.run()

# View the results
print(job_data.head())