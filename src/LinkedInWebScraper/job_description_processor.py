from OpenAIHandler.openai_handler import OpenAIHandler
from Utils.logger import Logger
import pandas as pd

class JobDescriptionProcessor:
    def __init__(self, openai_handler: OpenAIHandler, logger:Logger):
        """
        Initialize the JobDescriptionProcessor.

        Args:
            openai_handler (OpenAIHandler): An instance of the OpenAIHandler class to interact with the OpenAI API.
            logger (Logger): An instance of the Logger class to log the process.
        """
        self.openai_handler = openai_handler
        self.logger = logger

    def process_job_descriptions(self, df_jobs:pd.DataFrame):
        """
        Process job descriptions using the OpenAI API and add parsed fields to DataFrame.

        Args:
            df_jobs (pd.DataFrame): DataFrame containing job data with a 'Description' column.

        Returns:
            pd.DataFrame: DataFrame with additional parsed fields such as 'ShortDescription', 'TechStack', 'YoE', etc.
        """
        self.logger.log.info(f"Processing {len(df_jobs)} job descriptions using OpenAI API.")

        for index, row in df_jobs.iterrows():
            description = row['Description']
            
            # Create messages and generate a completion using the OpenAI handler
            messages = self.openai_handler.create_messages(description)
            response = self.openai_handler.generate_chat_completion(messages)
            
            # Add the parsed JSON fields into the DataFrame as new columns
            df_jobs.at[index, 'ShortDescription'] = response.get('Description', 'N/A')
            df_jobs.at[index, 'TechStack'] = ', '.join(response.get('TechStack', []))
            df_jobs.at[index, 'YoE'] = response.get('YoE', 'N/A')
            df_jobs.at[index, 'MinLevelStudies'] = response.get('MinLevelStudies', 'N/A')
            df_jobs.at[index, 'English'] = response.get('English', 'N/A')

        self.logger.log.info(f"Finished processing job descriptions.")
        return df_jobs
