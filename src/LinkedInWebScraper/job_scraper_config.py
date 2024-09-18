from Utils.logger import Logger

class JobScraperConfig:
    '''
    String representation of the job scraper configuration.

    Args:
        position (str): The job position to search for.
        location (str): The location to search for jobs.
        time_posted (str): The time frame in which the job was posted. Defaults to 'DAY'
        remote (str, optional): The remote work preference. Defaults to 'ALL'.
        distance (int, optional): The distance for the job search. Defaults to 10.

    Returns:
        str: A formatted string representing the JobScraperConfig object with its attributes.
    '''
    def __init__(self, position: str, location: str, openai_enabled: bool = False, time_posted: str = 'DAY', remote: str = 'ALL', distance: int = 10):
        self.position = position
        self.location = location
        self.openai_enabled = openai_enabled
        self.time_posted = time_posted
        self.remote = remote
        self.distance = distance

    def __str__(self):
        """String representation of the configuration."""
        return (f"JobScraperConfig(position={self.position}, location={self.location}, openai_enabled={self.openai_enabled}"
                f"time_posted={self.time_posted}, remote={self.remote}, distance={self.distance})")

