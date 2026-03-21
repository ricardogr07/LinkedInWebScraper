"""Optional OpenAI integration exports."""

from linkedin_web_scraper.infra.openai.job_description_processor import JobDescriptionProcessor
from linkedin_web_scraper.infra.openai.models import (
    JobDescriptionEnricher,
    JobDescriptionEnrichment,
    OpenAIEnrichmentConfig,
)
from linkedin_web_scraper.infra.openai.openai_handler import (
    OpenAIConfigurationError,
    OpenAIDependencyError,
    OpenAIHandler,
)

__all__ = [
    "JobDescriptionEnrichment",
    "JobDescriptionEnricher",
    "JobDescriptionProcessor",
    "OpenAIConfigurationError",
    "OpenAIDependencyError",
    "OpenAIEnrichmentConfig",
    "OpenAIHandler",
]
