from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from linkedin_web_scraper.infra.logging import Logger, resolve_logger


class OpenAIHandler:
    """Handle OpenAI interactions used for job description enrichment."""

    def __init__(self, logger: logging.Logger | Logger | None = None):
        self.logger = resolve_logger(logger, name=__name__)
        self.logger.info("Initializing OpenAI Handler")
        self._configure_openai()

    def _configure_openai(self) -> None:
        """Configure the OpenAI client from environment variables."""
        self.logger.info("Configuring OpenAI Client")

        try:
            load_dotenv()
            openai_api_key = os.environ.get("OPENAI_API_KEY")
        except Exception as error:
            self.logger.error("Error loading environment variables: %s", error)
            raise OSError("API Key is missing in .env file.") from error

        self.client = OpenAI(api_key=openai_api_key)

    def create_messages(self, description: str) -> list[dict[str, str]]:
        """Create the prompt payload for job description processing."""
        return [
            {
                "role": "system",
                "content": """You are an assistant that extracts structured data from job descriptions in JSON format. Please ensure the output matches the following keys: Description, TechStack, YoE, MinLevelStudies, and English. The English key should be a boolean (True/False) that indicates whether the position requires English language proficiency, if the initial job description is in English, assume English as a requirement. If the information is in a language other than English, translate it and use English in the description you parse to the JSON. Do not add information about the company in the Description, only include relevant information about the job. Add all relevant information about the techstack, including all languages and hard skills. Return only the JSON object as the output, without anything else before or after it.""",
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
    """,
            },
        ]

    def generate_chat_completion(self, messages: list[dict[str, str]]) -> dict:
        """Generate a JSON chat completion and parse it to a dictionary."""
        try:
            completion = self.client.chat.completions.create(
                messages=messages,
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
            )
            result = completion.choices[0].message.content
            return json.loads(result)
        except Exception:
            self.logger.exception("Unexpected error during OpenAI completion.")
            raise
