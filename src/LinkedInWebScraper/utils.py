import requests
import time
import random
from Utils.logger import Logger
from Utils.constants import USER_AGENT_HEADERS

def get_random_header():
    """Returns a random user-agent header from the list."""
    return random.choice(USER_AGENT_HEADERS)

def fetch_until_success(url, logger=None, max_retries=5, backoff_time=1):
    """
    Attempts to fetch jobs from a URL until success or maximum retries are reached.

    Args:
        url (str): The URL to fetch jobs from.
        logger (Logger, optional): Logger instance. Defaults to creating a new logger.
        max_retries (int, optional): Maximum number of retries before giving up. Defaults to 5.
        backoff_time (int or float, optional): Initial backoff time in seconds between retries. Defaults to 1 second.

    Returns:
        Response or None: Returns the response object if successful, otherwise None.
    """

    # Create a default logger if none is provided
    if logger is None:
        logger = Logger('fetch_jobs.log')

    retries = 0

    while retries < max_retries:
        try:
            # Log the attempt
            logger.log.debug(f"Attempting to fetch data from {url} (Attempt {retries + 1}/{max_retries})")

            # Send the request with a random user-agent header
            response = requests.get(url, headers=get_random_header(), timeout=10)
            
            # If the request is successful, return the response
            if response.status_code == 200:
                logger.log.debug(f"Successfully fetched data from {url}")
                return response
            
            # Log unsuccessful response
            logger.log.debug(f"Received status code {response.status_code} from {url}")
        
        except requests.exceptions.RequestException as e:
            logger.log.debug(f"Request error: {e}. Retrying... (Attempt {retries + 1}/{max_retries})")

        # Increment retry count
        retries += 1

        # Implement exponential backoff
        time.sleep(backoff_time)
        backoff_time = min(backoff_time * 2, 60)  # Cap backoff at 60 seconds
    
    # Log that maximum retries were reached
    logger.log.debug(f"Max retries reached. Unable to fetch jobs from {url}")
    return None