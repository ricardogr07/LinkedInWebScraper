import re
import pandas as pd

from Utils.logger import Logger
from Utils.constants import DATA_SCIENCE_KEYWORDS

class JobTitleClassifier:
    def __init__(self, logger: Logger, keywords: list = None):
        """
        Initialize the classifier with a list of keywords.

        Args:
            keywords (list): A list of keywords to classify job titles.
                             If None, a default list for data science-related jobs is used.
        """
        self.logger = logger
        if keywords is None:
            self.keywords = DATA_SCIENCE_KEYWORDS
            self.logger.log.info(f"Initialized JobTitleClassifier with default keywords: {self.keywords}")
        else:
            self.keywords = [keyword.lower() for keyword in keywords]
            self.logger.log.info(f"Initialized JobTitleClassifier with custom keywords: {self.keywords}")

    def classify_title(self, df_jobs):
        """
        Classify job titles based on keywords and filter out unrelated jobs.

        Args:
            df_jobs (pd.DataFrame): DataFrame containing job information, must include a 'Title' column.

        Returns:
            pd.DataFrame: Filtered DataFrame with only jobs related to the keywords.
        """
        if 'Title' not in df_jobs.columns:
            self.logger.log.error("The DataFrame does not contain a 'Title' column. No action will be performed.")
            return df_jobs

        self.logger.log.info(f"Starting classification of {len(df_jobs)} job titles.")

        df_jobs['DS_Related'] = df_jobs['Title'].apply(self._classify_single_title)

        related_jobs_count = df_jobs['DS_Related'].sum()
        self.logger.log.info(f"Classified {related_jobs_count} jobs as related to Data Science.")

        df_jobs = df_jobs.loc[df_jobs['DS_Related'] == 1].copy()
        df_jobs.drop(columns=['DS_Related'], inplace=True)

        self.logger.log.info(f"Returning DataFrame with {len(df_jobs)} data science-related jobs.")

        return df_jobs

    def _classify_single_title(self, title):
        """
        Classify a single job title by checking if it contains any of the keywords.

        Args:
            title (str): Job title to classify.

        Returns:
            int: 1 if the title contains any of the keywords, 0 otherwise.
        """
        title_lower = title.lower()

        for keyword in self.keywords:
            if re.search(rf'\b{keyword}\b', title_lower):
                self.logger.log.debug(f"Title '{title}' matches keyword '{keyword}'")
                return 1

        self.logger.log.debug(f"Title '{title}' does not match any keywords.")
        return 0
