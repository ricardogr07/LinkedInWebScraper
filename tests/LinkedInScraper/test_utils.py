import pytest
import requests
from Utils.logger import Logger
from Utils.constants import USER_AGENT_HEADERS
from unittest.mock import patch, MagicMock
from LinkedInScraper.utils import get_random_header, fetch_until_success

# Test get_random_header
def test_get_random_header():
    """Test that get_random_header returns a valid user-agent from the list."""
    header = get_random_header()
    assert header in USER_AGENT_HEADERS

# Test fetch_until_success
class TestFetchUntilSuccess:

    @pytest.fixture
    def logger(self):
        """Provides a mock logger instance."""
        mock_logger = MagicMock()
        mock_logger.log = MagicMock()
        return mock_logger

    @patch('requests.get')
    @patch('random.choice', return_value={'User-Agent': 'Mozilla/5.0'})
    def test_fetch_success_on_first_try(self, mock_random_choice, mock_requests_get, logger):
        """Test fetch_until_success succeeds on the first try."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        url = "http://example.com"
        response = fetch_until_success(url, logger=logger)

        # Assert the correct URL and headers were used
        mock_requests_get.assert_called_once_with(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)

        # Assert success on first attempt
        assert response == mock_response
        logger.log.debug.assert_called_with(f"Successfully fetched data from {url}")

    @patch('requests.get')
    @patch('time.sleep', return_value=None)  # Mock time.sleep to avoid actual delays
    def test_fetch_retries_on_failure(self, mock_sleep, mock_requests_get, logger):
        """Test fetch_until_success retries on failure with status code other than 200."""
        # Simulate failed responses (status codes != 200)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_requests_get.return_value = mock_response

        url = "http://example.com"
        max_retries = 3
        response = fetch_until_success(url, logger=logger, max_retries=max_retries)

        # Ensure requests.get was called max_retries times
        assert mock_requests_get.call_count == max_retries
        assert response is None  # Should return None after failing all retries

        # Ensure the logger logged the retries
        logger.log.debug.assert_any_call(f"Received status code 500 from {url}")
        logger.log.debug.assert_any_call(f"Max retries reached. Unable to fetch jobs from {url}")

    @patch('requests.get')
    @patch('time.sleep', return_value=None)  # Mock time.sleep to avoid delays
    def test_fetch_handles_request_exception(self, mock_sleep, mock_requests_get, logger):
        """Test fetch_until_success handles RequestException and retries."""
        # Simulate request exception (e.g., connection error)
        mock_requests_get.side_effect = requests.exceptions.RequestException

        url = "http://example.com"
        max_retries = 2
        response = fetch_until_success(url, logger=logger, max_retries=max_retries)

        # Ensure requests.get was called max_retries times
        assert mock_requests_get.call_count == max_retries
        assert response is None  # Should return None after all retries

        # Ensure the logger logged the exception and retries
        logger.log.debug.assert_any_call(f"Request error: . Retrying... (Attempt 1/{max_retries})")
        logger.log.debug.assert_any_call(f"Max retries reached. Unable to fetch jobs from {url}")

    @patch('requests.get')
    @patch('time.sleep', return_value=None)  # Mock time.sleep to avoid delays
    def test_fetch_exponential_backoff(self, mock_sleep, mock_requests_get, logger):
        """Test that fetch_until_success uses exponential backoff between retries."""
        # Simulate failed responses
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_requests_get.return_value = mock_response

        url = "http://example.com"
        max_retries = 3
        initial_backoff = 2
        fetch_until_success(url, logger=logger, max_retries=max_retries, backoff_time=initial_backoff)

        # Ensure requests.get was called max_retries times
        assert mock_requests_get.call_count == max_retries

        # Check that time.sleep was called with the correct backoff intervals
        expected_backoff_times = [initial_backoff, initial_backoff * 2, initial_backoff * 4]  # 2, 4, 8 seconds
        actual_backoff_times = [call[0][0] for call in mock_sleep.call_args_list]
        
        assert actual_backoff_times == expected_backoff_times

