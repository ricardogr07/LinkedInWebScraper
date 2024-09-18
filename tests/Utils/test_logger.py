import pytest
import logging
from Utils.logger import Logger

class TestLogger:

    def setup_method(self):
        logging.shutdown()
        # Reset any existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    def test_logger_singleton_behavior(self, mocker):
        mock_basicConfig = mocker.patch('logging.basicConfig')
        mock_getLogger = mocker.patch('logging.getLogger')
        filename1 = 'log1.log'
        filename2 = 'log2.log'

        logger_instance1 = Logger(filename1)
        logger_instance2 = Logger(filename2)

        # Both instances should be the same (singleton pattern)
        assert logger_instance1 is logger_instance2

    def test_logger_writes_to_correct_file(self, mocker):
        mock_basicConfig = mocker.patch('logging.basicConfig')
        mock_getLogger = mocker.patch('logging.getLogger')
        mock_file_handler = mocker.patch('logging.FileHandler')

        filename = 'test.log'
        Logger(filename)

        # Ensure basicConfig is called with force=True
        mock_basicConfig.assert_called_once_with(
            filename=filename,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            force=True
        )

    def test_logger_initialized_only_once(self, mocker):
        mock_basicConfig = mocker.patch('logging.basicConfig')
        mock_getLogger = mocker.patch('logging.getLogger')
        filename1 = 'log1.log'
        filename2 = 'log2.log'

        logger_instance1 = Logger(filename1)
        logger_instance2 = Logger(filename2)

        # Ensure basicConfig is called only once
        mock_basicConfig.assert_called_once_with(
            filename=filename1,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            force=True
        )
        # Ensure basicConfig isn't called again
        mock_basicConfig.assert_called_once()

    def test_logger_writes_to_console_and_file(self, mocker):
        logging.shutdown()

        # Patch the necessary components
        mock_basicConfig = mocker.patch('logging.basicConfig')
        mock_logger_instance = mocker.Mock()
        mock_getLogger = mocker.patch('logging.getLogger', return_value=mock_logger_instance)
        mock_stream_handler = mocker.patch('logging.StreamHandler')

        filename = 'test.log'
        Logger(filename)

        # Ensure the stream handler is added to the logger
        mock_stream_handler.assert_called_once()
        mock_logger_instance.addHandler.assert_called_with(mock_stream_handler())

    def test_logger_singleton_persists_across_calls(self, mocker):
        mock_basicConfig = mocker.patch('logging.basicConfig')
        mock_getLogger = mocker.patch('logging.getLogger')

        filename1 = 'log1.log'
        filename2 = 'log2.log'

        logger_instance1 = Logger(filename1)
        logger_instance2 = Logger(filename2)

        # Assert that both instances are the same (singleton)
        assert logger_instance1 is logger_instance2

        # Ensure basicConfig was called once
        mock_basicConfig.assert_called_once_with(
            filename=filename1,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            force=True
        )

    def test_logger_respects_logging_levels(self, mocker):
        mock_basicConfig = mocker.patch('logging.basicConfig')
        mock_logger_instance = mocker.Mock()
        mock_getLogger = mocker.patch('logging.getLogger', return_value=mock_logger_instance)

        filename = 'test.log'
        Logger(filename)

        # Log an error message
        error_message = "This is a test error message."
        Logger(filename).log.error(error_message)

        # Ensure the log.error method is called with the correct message
        mock_logger_instance.error.assert_called_once_with(error_message)

    def test_logger_instance_creation_with_valid_filename(self, mocker):
        mock_basicConfig = mocker.patch('logging.basicConfig')
        mock_getLogger = mocker.patch('logging.getLogger')

        filename = 'test.log'
        Logger(filename)

        # Ensure basicConfig is called with the correct arguments
        mock_basicConfig.assert_called_once_with(
            filename=filename,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            force=True
        )

    def test_logger_instance_creation_with_empty_filename(self, mocker):
        mock_basicConfig = mocker.patch('logging.basicConfig')
        mock_getLogger = mocker.patch('logging.getLogger')
        filename = ''

        Logger(filename)

        # Ensure basicConfig is called with an empty filename
        mock_basicConfig.assert_called_once_with(
            filename=filename,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            force=True
        )
        mock_getLogger.assert_called_once()
