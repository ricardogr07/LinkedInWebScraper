class JobScraperAdvancedConfig:
    """
    A configuration class for advanced job scraping settings.

    Attributes:
        LOCATION_MAPPING (dict): A dictionary mapping location names to their respective codes or identifiers.
        KEYWORDS (list): A list of keywords to search for in job titles and descriptions.
        SKILLS_CATEGORIES (dict): A dictionary categorizing skills relevant to job postings.
    """

    def __init__(self, LOCATION_MAPPING: dict = None, KEYWORDS: list = None, SKILLS_CATEGORIES: dict = None):
        """
        Initializes the JobScraperAdvancedConfig with specific settings.

        Args:
            LOCATION_MAPPING (dict, optional): A dictionary mapping location names to codes or identifiers.
            KEYWORDS (list, optional): A list of keywords used for searching job titles and descriptions.
            SKILLS_CATEGORIES (dict, optional): A dictionary categorizing skills related to job postings.

        Notes:
            If any of the parameters are passed as None, they will be initialized to an empty dictionary or list.
        """
        # Assign parameters to instance variables, defaulting to empty structures if None
        self.LOCATION_MAPPING = LOCATION_MAPPING
        self.KEYWORDS = KEYWORDS
        self.SKILLS_CATEGORIES = SKILLS_CATEGORIES

    def __str__(self) -> str:
        """
        Returns a string representation of the configuration.

        Returns:
            str: A string detailing the configuration settings.
        """
        return (f"JobScraperAdvancedConfig(LOCATION_MAPPING={self.LOCATION_MAPPING}, "
                f"KEYWORDS={self.KEYWORDS}, SKILLS_CATEGORIES={self.SKILLS_CATEGORIES})")
