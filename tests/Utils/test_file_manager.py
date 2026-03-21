from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from LinkedInWebScraper.job_scraper_config import JobScraperConfig
from Utils.file_manager import FileManager
from Utils.logger import Logger


@pytest.fixture
def logger():
    mock_logger = MagicMock(Logger)
    mock_logger.log = MagicMock()
    return mock_logger


@pytest.fixture
def config():
    return JobScraperConfig(
        position="Data Scientist", location="New York", time_posted="WEEK", remote="REMOTE"
    )


@pytest.fixture
def file_manager(logger, config):
    return FileManager(logger, config)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "JobID": ["12345", "67890"],
            "Title": ["Data Scientist", "Senior Data Scientist"],
            "Company": ["Company A", "Company B"],
            "Location": ["New York", "Remote"],
            "Url": ["http://example.com/12345", "http://example.com/67890"],
        }
    )


class TestFileManager:
    def test_initialization(self, file_manager, config):
        assert file_manager.position == config.position
        assert file_manager.location == config.location
        assert file_manager.time_posted == config.time_posted
        assert file_manager.remote == config.remote

    @patch("Utils.file_manager.datetime")
    def test_generate_file_name(self, mock_datetime, file_manager):
        mock_datetime.now.return_value = datetime(2024, 9, 15)
        expected_file_name = "LinkedIn_Jobs_Data_Scientist_New_York_LAST_WEEK_REMOTE_2024-09-15.csv"
        assert file_manager.generate_file_name() == expected_file_name

    @patch("pandas.DataFrame.to_csv")
    @patch("os.path.exists", return_value=False)
    def test_save_jobs_to_csv_new_file(self, mock_exists, mock_to_csv, file_manager, sample_df):
        file_manager.save_jobs_to_csv(sample_df, append=False)

        expected_file_name = file_manager.generate_file_name()
        mock_to_csv.assert_called_once_with(expected_file_name, index=False)

    @patch("pandas.read_csv")
    @patch("pandas.DataFrame.to_csv")
    @patch("os.path.exists", return_value=True)
    def test_append_jobs_to_csv(
        self, mock_exists, mock_to_csv, mock_read_csv, file_manager, sample_df
    ):
        existing_df = pd.DataFrame(
            {
                "JobID": ["12345"],
                "Title": ["Data Scientist"],
                "Company": ["Company A"],
                "Location": ["New York"],
                "Url": ["http://example.com/12345"],
            }
        )
        mock_read_csv.return_value = existing_df
        file_manager.append_jobs_to_csv(sample_df, "test_file.csv")

        mock_to_csv.assert_called_once()
        file_manager.logger.info.assert_called_with(
            "Appended %s new jobs to %s.", 1, "test_file.csv"
        )

    @patch("pandas.read_csv")
    @patch("os.path.exists", return_value=True)
    def test_no_new_jobs_to_append(self, mock_exists, mock_read_csv, file_manager, sample_df):
        mock_read_csv.return_value = sample_df
        file_manager.append_jobs_to_csv(sample_df, "test_file.csv")

        file_manager.logger.info.assert_called_with("No new jobs to append to %s.", "test_file.csv")

    def test_clean_job_ids(self, file_manager, sample_df):
        sample_df_dirty = pd.DataFrame(
            {
                "JobID": [" 12345 ", "67890 "],
                "Title": ["Data Scientist", "Senior Data Scientist"],
                "Company": ["Company A", "Company B"],
                "Location": ["New York", "Remote"],
                "Url": ["http://example.com/12345", "http://example.com/67890"],
            }
        )

        cleaned_df = file_manager.clean_job_ids(sample_df_dirty)
        assert cleaned_df["JobID"].tolist() == ["12345", "67890"]
