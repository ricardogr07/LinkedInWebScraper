import time

from linkedin_web_scraper.application.daily_scrape_service import DailyScrapeService
from Utils.logger import Logger

if __name__ == "__main__":
    overall_start_time = time.time()

    logger = Logger("main.log")
    DailyScrapeService(logger=logger).run_daily()

    overall_end_time = time.time()
    overall_duration = overall_end_time - overall_start_time
    logger.log.info(f"main.py wrapper completed in {overall_duration:.2f} seconds.")
