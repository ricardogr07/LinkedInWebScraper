from process_ds_jobs import run_ds_daily_scraper
from Utils.logger import Logger
import pandas as pd
import time

if __name__ == '__main__':
    overall_start_time = time.time()

    cities = ['Monterrey', 'Guadalajara', 'Mexico City']

    logger = Logger('main.log')

    logger.log.info(f'Initializing web scraping for LinkedIn Jobs for the cities {cities}.')

    for city in cities:
        city_start_time = time.time()
        city_filename = city.replace(" ", "_")
        file = f'LinkedIn_Jobs_Data_Scientist_{city_filename}.csv'
        run_ds_daily_scraper(logger=logger, location=city, file_name=file)

        city_end_time = time.time()
        city_duration = city_end_time - city_start_time
        logger.log.info(f'Finished web scraping for {city}. It took {city_duration:.2f} seconds.')


    df_mty = pd.read_csv('LinkedIn_Jobs_Data_Scientist_Monterrey.csv')
    df_gdl = pd.read_csv('LinkedIn_Jobs_Data_Scientist_Guadalajara.csv')
    df_cdmx = pd.read_csv('LinkedIn_Jobs_Data_Scientist_Mexico_City.csv')

    df_jobs_all = pd.concat([df_mty, df_gdl, df_cdmx], ignore_index=True)
    df_jobs_all.to_csv('LinkedIn_Jobs_Data_Scientist_Mexico.csv', index=False)
    logger.log.info('Saved the final concatenated jobs data to LinkedIn_Jobs_Data_Scientist_Mexico.csv.')

    overall_end_time = time.time()
    overall_duration = overall_end_time - overall_start_time
    logger.log.info(f'Web scraping for all cities completed in {overall_duration:.2f} seconds.')
