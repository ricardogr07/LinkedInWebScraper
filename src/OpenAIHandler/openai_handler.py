from linkedin_web_scraper._compat import warn_legacy_namespace
from linkedin_web_scraper.infra.openai.openai_handler import OpenAIHandler

warn_legacy_namespace("OpenAIHandler.openai_handler")

__all__ = ["OpenAIHandler"]