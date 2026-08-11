from linkedin_web_scraper import JobScraperConfig, LinkedInJobScraper, Logger

logger = Logger("example_openai.log")

# Define scraper configuration
config = JobScraperConfig(
    position="Data Analyst",
    location="San Francisco",
    remote="REMOTE",
    enrichment_provider="OPENAI",
    enrichment_model="gpt-4o-mini",
)

# Initialize the scraper
scraper = LinkedInJobScraper(logger, config)

# Scrape job data
job_data = scraper.run()

# View the results
print(job_data.head())
