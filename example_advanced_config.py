from LinkedInWebScraper import LinkedInJobScraper, JobScraperConfig, JobScraperAdvancedConfig, Logger

logger = Logger('example_advanced_config.log')

KEYWORDS_LIST = [
                    'data', 'analytics', 'business intelligence', 'bi',
                    'statistical', 'statistics', 'analysis', 'power bi'
                ]

advanced_config = JobScraperAdvancedConfig(KEYWORDS=KEYWORDS_LIST)

# Define scraper configuration
config = JobScraperConfig(
    position="Data Analyst",
    location="San Francisco",
    remote="REMOTE", 
    advanced_config=advanced_config
)

# Initialize the scraper
scraper = LinkedInJobScraper(logger,config)

# Scrape job data
job_data = scraper.run()

# View the results
print(job_data.head())