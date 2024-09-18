from Utils.logger import Logger
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIHandler:
    """
    A class for handling interactions with OpenAI services.

    Attributes:
        logger (Logger) (Optional): The logger object for logging messages.
        client (OpenAI): The OpenAI client for API interactions.

    Methods:
        create_messages: Creates a list of messages for processing job descriptions.
        generate_chat_completion: Generates chat completions using the OpenAI client and returns the parsed result.
    """
    def __init__(self, logger=None):
        """
        Initialize the OpenAIHandler with a logger instance and configure the OpenAI client 
        by loading the API key from environment variables.
        
        """
        self.logger = logger if logger is not None else Logger("openai.log")
        self.logger.log.info("Initializing OpenAI Handler")
        self._configure_openai()


    def _configure_openai(self):
        '''
        Configures the OpenAI client by loading the API key from environment variables. 
        If an error occurs while loading the environment variables, an EnvironmentError is raised 
        indicating that the API Key is missing in the .env file.
        '''
        self.logger.log.info("Configuring OpenAI Client")

        try:
            load_dotenv()
            OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
        except Exception as e:
            self.logger.log.error(f"Error loading environment variables: {e}")
            raise EnvironmentError("API Key is missing in .env file.")        
        
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

    def create_messages(self, description: str) -> list:
        '''
        Creates a list of messages for processing job descriptions.

        Parameters:
            description (str): The job description to be processed.

        Returns:
            list: A list containing system and user messages for job description processing.
        '''
        return [
            {
                "role": "system",
                "content": """You are an assistant that extracts structured data from job descriptions in JSON format. Please ensure the output matches the following keys: Description, TechStack, YoE, MinLevelStudies, and English. The English key should be a boolean (True/False) that indicates whether the position requires English language proficiency, if the initial job description is in English, assume English as a requirement. If the information is in a language other than English, translate it and use English in the description you parse to the JSON. Do not add information about the company in the Description, only include relevant information about the job. Add all relevant information about the techstack, including all languages and hard skills. Return only the JSON object as the output, without anything else before or after it."""
            },
            {
                "role": "user",
                "content": f"""Here's an example of how I want the job description processed:
        Job Description:
        "The main challenge for the Artificial Intelligence Developer is to develop and implement advanced AI solutions that optimize educational and administrative processes. This position requires the ability to apply cutting-edge AI technologies to enhance learning quality, automate administrative processes, and support data-driven decision-making, driving innovation and efficiency in the institution."

        Output:
        {{
        "Description": "The main challenge for the Artificial Intelligence Developer is to develop and implement advanced AI solutions that optimize processes, improve learning quality, and support decision-making through data-driven technologies.",
        "TechStack": ["Python", "R", "SQL", "NoSQL", "Agile Methodologies"],
        "YoE": "N/A",
        "MinLevelStudies": "N/A",
        "English": True
        }}

    Now process this new job description:
    "{description}"
    """
            }
        ]


    def generate_chat_completion(self, messages: list) -> dict:
        '''
        Generates chat completions using the OpenAI client and returns the parsed result.

        Parameters:
            messages (list): A list of messages for chat completion generation.

        Returns:
            json (dict): The parsed result obtained from the chat completion process in JSON format.

        Raises:
            Exception: If an unexpected error occurs during the chat completion generation process.
        ''' 
        try:
            completion = self.client.chat.completions.create(
                messages=messages,
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
            )
            result = completion.choices[0].message.content
            parsed_result = json.loads(result)
       
            return parsed_result
        
        except Exception as e:
            self.logger.log.error(f"Unexpected error: {e}")
            raise