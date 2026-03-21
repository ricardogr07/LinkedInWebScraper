from __future__ import annotations

import random
import time

import requests

from linkedin_web_scraper.config.constants import USER_AGENT_HEADERS
from linkedin_web_scraper.infra.logging import resolve_logger


def get_random_header() -> dict[str, str]:
    """Return a random user-agent header from the configured list."""
    return random.choice(USER_AGENT_HEADERS)


def fetch_until_success(
    url: str,
    logger=None,
    max_retries: int = 5,
    backoff_time: float = 1,
    *,
    session: requests.Session | None = None,
    timeout: float = 10,
):
    """Attempt to fetch a URL until success or the retry budget is exhausted."""
    active_logger = resolve_logger(logger, name=__name__)
    request_get = session.get if session is not None else requests.get

    retries = 0
    while retries < max_retries:
        try:
            active_logger.debug(
                "Attempting to fetch data from %s (Attempt %s/%s)",
                url,
                retries + 1,
                max_retries,
            )
            response = request_get(url, headers=get_random_header(), timeout=timeout)

            if response.status_code == 200:
                active_logger.debug("Successfully fetched data from %s", url)
                return response

            active_logger.debug("Received status code %s from %s", response.status_code, url)

        except requests.exceptions.RequestException as error:
            active_logger.debug(
                "Request error: %s. Retrying... (Attempt %s/%s)",
                error,
                retries + 1,
                max_retries,
            )

        retries += 1
        time.sleep(backoff_time)
        backoff_time = min(backoff_time * 2, 60)

    active_logger.debug("Max retries reached. Unable to fetch jobs from %s", url)
    return None
