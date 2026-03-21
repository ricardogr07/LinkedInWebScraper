from __future__ import annotations

import random
import time
from collections.abc import Callable, Sequence

import requests

from linkedin_web_scraper.config.constants import USER_AGENT_HEADERS
from linkedin_web_scraper.infra.http.policy import HttpRequestPolicy
from linkedin_web_scraper.infra.logging import resolve_logger


def get_random_header(headers: Sequence[dict[str, str]] | None = None) -> dict[str, str]:
    """Return a random user-agent header from the configured list."""
    return random.choice(list(headers or USER_AGENT_HEADERS))


def fetch_until_success(
    url: str,
    logger=None,
    max_retries: int | None = None,
    backoff_time: float | None = None,
    *,
    session: requests.Session | None = None,
    timeout: float | None = None,
    policy: HttpRequestPolicy | None = None,
    sleep: Callable[[float], None] | None = None,
):
    """Attempt to fetch a URL until success or the retry budget is exhausted."""
    active_logger = resolve_logger(logger, name=__name__)
    request_policy = policy or HttpRequestPolicy()
    request_policy = request_policy.with_overrides(
        timeout=timeout,
        max_retries=max_retries,
        initial_backoff=backoff_time,
    )
    request_get = session.get if session is not None else requests.get
    sleep_fn = sleep or time.sleep

    current_backoff = request_policy.initial_backoff
    for attempt in range(1, request_policy.max_retries + 1):
        try:
            active_logger.debug(
                "Attempting to fetch data from %s (Attempt %s/%s)",
                url,
                attempt,
                request_policy.max_retries,
            )
            response = request_get(
                url,
                headers=get_random_header(request_policy.user_agent_headers),
                timeout=request_policy.timeout,
            )

            if response.status_code == 200:
                active_logger.debug("Successfully fetched data from %s", url)
                return response

            active_logger.debug("Received status code %s from %s", response.status_code, url)
            if response.status_code not in request_policy.retryable_status_codes:
                active_logger.debug(
                    "Status code %s is not retryable for %s",
                    response.status_code,
                    url,
                )
                return None

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            active_logger.debug(
                "Request error: %s. Retrying... (Attempt %s/%s)",
                error,
                attempt,
                request_policy.max_retries,
            )
        except requests.exceptions.RequestException as error:
            active_logger.debug(
                "Request failed without retry: %s (Attempt %s/%s)",
                error,
                attempt,
                request_policy.max_retries,
            )
            return None

        if attempt == request_policy.max_retries:
            break

        sleep_fn(current_backoff)
        current_backoff = min(
            max(current_backoff * 2, current_backoff),
            request_policy.max_backoff,
        )

    active_logger.debug("Max retries reached. Unable to fetch jobs from %s", url)
    return None