"""Optional OpenAI integration exports."""

from linkedin_web_scraper.infra.openai.job_description_processor import JobDescriptionProcessor
from linkedin_web_scraper.infra.openai.openai_handler import OpenAIHandler

__all__ = ["OpenAIHandler", "JobDescriptionProcessor"]
