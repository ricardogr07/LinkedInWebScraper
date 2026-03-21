from unittest.mock import MagicMock, patch

import pytest
import requests

from LinkedInWebScraper.utils import fetch_until_success, get_random_header
from Utils.constants import USER_AGENT_HEADERS


def test_get_random_header():
    header = get_random_header()
    assert header in USER_AGENT_HEADERS


class TestFetchUntilSuccess:
    @pytest.fixture
    def logger(self):
        mock_logger = MagicMock()
        mock_logger.log = MagicMock()
        return mock_logger

    @patch("requests.get")
    @patch("random.choice", return_value={"User-Agent": "Mozilla/5.0"})
    def test_fetch_success_on_first_try(self, mock_random_choice, mock_requests_get, logger):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        url = "http://example.com"
        response = fetch_until_success(url, logger=logger)

        mock_requests_get.assert_called_once_with(
            url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        )
        assert response == mock_response
        logger.log.debug.assert_any_call("Successfully fetched data from %s", url)

    @patch("requests.get")
    @patch("time.sleep", return_value=None)
    def test_fetch_retries_on_failure(self, mock_sleep, mock_requests_get, logger):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_requests_get.return_value = mock_response

        url = "http://example.com"
        max_retries = 3
        response = fetch_until_success(url, logger=logger, max_retries=max_retries)

        assert mock_requests_get.call_count == max_retries
        assert response is None
        logger.log.debug.assert_any_call("Received status code %s from %s", 500, url)
        logger.log.debug.assert_any_call("Max retries reached. Unable to fetch jobs from %s", url)

    @patch("requests.get")
    @patch("time.sleep", return_value=None)
    def test_fetch_handles_request_exception(self, mock_sleep, mock_requests_get, logger):
        mock_requests_get.side_effect = requests.exceptions.RequestException

        url = "http://example.com"
        max_retries = 2
        response = fetch_until_success(url, logger=logger, max_retries=max_retries)

        assert mock_requests_get.call_count == max_retries
        assert response is None
        request_error_calls = [
            call
            for call in logger.log.debug.call_args_list
            if call.args and call.args[0] == "Request error: %s. Retrying... (Attempt %s/%s)"
        ]
        assert request_error_calls
        assert isinstance(request_error_calls[0].args[1], requests.exceptions.RequestException)
        assert request_error_calls[0].args[2:] == (1, max_retries)
        logger.log.debug.assert_any_call("Max retries reached. Unable to fetch jobs from %s", url)

    @patch("requests.get")
    @patch("time.sleep", return_value=None)
    def test_fetch_exponential_backoff(self, mock_sleep, mock_requests_get, logger):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_requests_get.return_value = mock_response

        url = "http://example.com"
        max_retries = 3
        initial_backoff = 2
        fetch_until_success(
            url, logger=logger, max_retries=max_retries, backoff_time=initial_backoff
        )

        assert mock_requests_get.call_count == max_retries
        assert [call[0][0] for call in mock_sleep.call_args_list] == [2, 4, 8]

