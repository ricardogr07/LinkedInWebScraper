import logging

class Logger:
    """
    A singleton class for logging messages to a file and the console.

    Args:
        filename (str): The name of the log file.

    Attributes:
        log (logging.Logger): The logger object.

    """

    _instance = None

    def __new__(cls, filename: str):
        """
        Ensures only one instance of the Logger class is created.

        Args:
            filename (str): The name of the log file.

        Returns:
            Logger: The singleton instance of Logger.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, filename: str):
        """
        Initializes a new instance of the Logger class if not already created.

        Args:
            filename (str): The name of the log file.
        """

        if not hasattr(self, 'log'):
            logging.basicConfig(filename=filename, level=logging.INFO,
                                format='%(asctime)s %(levelname)s %(message)s', force=True)
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            self.log = logging.getLogger()
            self.log.addHandler(stream_handler)
