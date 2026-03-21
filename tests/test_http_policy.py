from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
from linkedin_web_scraper.infra.http.job_scraper import JobScraper
from linkedin_web_scraper.infra.http.policy import HttpRequestPolicy
from linkedin_web_scraper.infra.http.utils import fetch_until_success, get_random_header


def test_get_random_header_uses_supplied_headers():
    headers = [{"User-Agent": "Mozilla/5.0"}]

    with patch("random.choice", return_value=headers[0]) as mock_random_choice:
        assert get_random_header(headers) == headers[0]

    mock_random_choice.assert_called_once_with(headers)


def test_http_request_policy_supports_overrides():
    policy = HttpRequestPolicy(timeout=5, max_retries=3, initial_backoff=2, max_backoff=10)

    overridden = policy.with_overrides(timeout=7, max_retries=4, retryable_status_codes=(500,))

    assert overridden.timeout == 7
    assert overridden.max_retries == 4
    assert overridden.initial_backoff == 2
    assert overridden.max_backoff == 10
    assert overridden.retryable_status_codes == (500,)


@patch("random.choice", return_value={"User-Agent": "Mozilla/5.0"})
def test_fetch_until_success_uses_session_and_policy(mock_random_choice):
    session = MagicMock()
    response = MagicMock(status_code=200)
    session.get.return_value = response
    policy = HttpRequestPolicy(
        timeout=7, max_retries=2, user_agent_headers=({"User-Agent": "Mozilla/5.0"},)
    )

    result = fetch_until_success(
        "http://example.com",
        logger=logging.getLogger("phase3-http"),
        session=session,
        policy=policy,
        sleep=lambda _: None,
    )

    assert result is response
    session.get.assert_called_once_with(
        "http://example.com",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=7,
    )


@patch("random.choice", return_value={"User-Agent": "Mozilla/5.0"})
def test_fetch_until_success_caps_backoff_with_policy(mock_random_choice):
    session = MagicMock()
    session.get.return_value = MagicMock(status_code=500)
    sleep_calls = []
    policy = HttpRequestPolicy(
        max_retries=4,
        initial_backoff=2,
        max_backoff=3,
        user_agent_headers=({"User-Agent": "Mozilla/5.0"},),
    )

    fetch_until_success(
        "http://example.com",
        logger=logging.getLogger("phase3-http-backoff"),
        session=session,
        policy=policy,
        sleep=sleep_calls.append,
    )

    assert sleep_calls == [2, 3, 3]


@patch("random.choice", return_value={"User-Agent": "Mozilla/5.0"})
def test_fetch_until_success_retries_503_and_does_not_sleep_after_last_attempt(mock_random_choice):
    session = MagicMock()
    session.get.return_value = MagicMock(status_code=503)
    sleep_calls = []
    policy = HttpRequestPolicy(
        max_retries=3,
        initial_backoff=1,
        max_backoff=5,
        retryable_status_codes=(503,),
        user_agent_headers=({"User-Agent": "Mozilla/5.0"},),
    )

    result = fetch_until_success(
        "http://example.com",
        logger=logging.getLogger("phase3-http-retryable"),
        session=session,
        policy=policy,
        sleep=sleep_calls.append,
    )

    assert result is None
    assert session.get.call_count == 3
    assert sleep_calls == [1, 2]


@patch("random.choice", return_value={"User-Agent": "Mozilla/5.0"})
def test_fetch_until_success_does_not_retry_404(mock_random_choice):
    session = MagicMock()
    session.get.return_value = MagicMock(status_code=404)
    sleep_calls = []
    policy = HttpRequestPolicy(
        max_retries=3,
        retryable_status_codes=(503,),
        user_agent_headers=({"User-Agent": "Mozilla/5.0"},),
    )

    result = fetch_until_success(
        "http://example.com",
        logger=logging.getLogger("phase3-http-404"),
        session=session,
        policy=policy,
        sleep=sleep_calls.append,
    )

    assert result is None
    assert session.get.call_count == 1
    assert sleep_calls == []


def test_job_scraper_preserves_supplied_policy_timeout_when_no_override_is_passed():
    policy = HttpRequestPolicy(timeout=17, max_retries=4)

    scraper = JobScraper(
        config=JobScraperConfig(position="Data Scientist", location="Monterrey"),
        request_policy=policy,
    )

    assert scraper.request_policy.timeout == 17
    assert scraper.request_timeout == 17


@patch("linkedin_web_scraper.infra.http.job_scraper.requests.Session")
def test_job_scraper_creates_and_reuses_default_session_when_none_is_injected(mock_session_factory):
    session = MagicMock()
    mock_session_factory.return_value = session

    scraper = JobScraper(config=JobScraperConfig(position="Data Scientist", location="Monterrey"))

    assert scraper.session is session

    response = MagicMock()
    response.text = '<span class="results-context-header__job-count">20</span>'
    with patch(
        "linkedin_web_scraper.infra.http.job_scraper.fetch_until_success",
        return_value=response,
    ) as fetch_mock:
        assert scraper.fetch_total_jobs() == 20

    assert fetch_mock.call_args.kwargs["session"] is session


def test_job_scraper_explicit_request_timeout_overrides_policy_timeout():
    policy = HttpRequestPolicy(timeout=17, max_retries=4)

    scraper = JobScraper(
        config=JobScraperConfig(position="Data Scientist", location="Monterrey"),
        request_policy=policy,
        request_timeout=9,
    )

    assert scraper.request_policy.timeout == 9
    assert scraper.request_timeout == 9


def test_job_scraper_passes_request_policy_to_fetches():
    logger = logging.getLogger("phase3-job-scraper")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    session = MagicMock()
    policy = HttpRequestPolicy(timeout=17, max_retries=4)
    scraper = JobScraper(
        config=JobScraperConfig(position="Data Scientist", location="Monterrey"),
        logger=logger,
        session=session,
        request_policy=policy,
    )

    response = MagicMock()
    response.text = '<span class="results-context-header__job-count">20</span>'

    with patch(
        "linkedin_web_scraper.infra.http.job_scraper.fetch_until_success",
        return_value=response,
    ) as fetch_mock:
        assert scraper.fetch_total_jobs() == 20

    fetch_mock.assert_called_once()
    assert fetch_mock.call_args.kwargs["session"] is session
    assert fetch_mock.call_args.kwargs["policy"] is scraper.request_policy
    assert scraper.request_timeout == scraper.request_policy.timeout
