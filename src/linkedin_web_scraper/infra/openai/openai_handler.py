"""Optional OpenAI adapter built on the Responses API."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL
from linkedin_web_scraper.infra.logging import Logger, resolve_logger
from linkedin_web_scraper.infra.openai.models import (
    NOT_AVAILABLE,
    SYSTEM_PROMPT,
    EnrichmentDependencyError,
    JobDescriptionEnrichment,
    OpenAIEnrichmentConfig,
    load_response_schema,
)


class OpenAIConfigurationError(RuntimeError):
    """Raised when OpenAI enrichment is requested without valid configuration."""


class OpenAIDependencyError(EnrichmentDependencyError):
    """Raised when optional OpenAI enrichment dependencies are missing."""


@lru_cache(maxsize=1)
def _load_openai_client_class() -> type[Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise OpenAIDependencyError(
            "OpenAI enrichment requires the optional dependencies installed via `.[openai]`."
        ) from exc
    return OpenAI


class OpenAIHandler:
    """Handle optional OpenAI job-description enrichment using structured parsing."""

    def __init__(
        self,
        logger: logging.Logger | Logger | None = None,
        *,
        model: str = DEFAULT_OPENAI_MODEL,
        api_key: str | None = None,
        client: Any | None = None,
    ):
        self.logger = resolve_logger(logger, name=__name__)
        self.config = OpenAIEnrichmentConfig(model=model, api_key=api_key)
        self.client = client or self._configure_openai()

    def _configure_openai(self) -> Any:
        """Create an OpenAI client from the explicit config or environment variables."""
        api_key = self._resolve_api_key()
        client_class = _load_openai_client_class()
        self.logger.info("Configuring OpenAI client for model %s.", self.config.model)
        return client_class(api_key=api_key)

    def _resolve_api_key(self) -> str:
        """Resolve the OpenAI API key from the handler config or environment."""
        if self.config.api_key is not None:
            return self.config.api_key

        openai_api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not openai_api_key:
            raise OpenAIConfigurationError(
                "OpenAI enrichment requires `OPENAI_API_KEY` in the environment or an injected client."
            )
        return openai_api_key

    def create_messages(self, description: str) -> list[dict[str, str]]:
        """Create a compatibility prompt payload for a raw job description."""
        normalized_description = str(description).strip()
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": normalized_description},
        ]

    def extract_job_description(self, description: str) -> JobDescriptionEnrichment:
        """Return structured enrichment data for a single job description."""
        normalized_description = str(description).strip()
        if not normalized_description:
            return JobDescriptionEnrichment()

        response = self.client.responses.parse(
            model=self.config.model,
            input=self.create_messages(normalized_description),
            text_format=load_response_schema(),
        )
        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            raise RuntimeError("OpenAI response did not include a parsed structured payload.")

        raw_payload = parsed.model_dump(mode="json")
        tech_stack = tuple(
            item.strip() for item in raw_payload.get("tech_stack", []) if str(item).strip()
        )

        return JobDescriptionEnrichment(
            short_description=self._normalize_text(raw_payload.get("description")),
            tech_stack=tech_stack,
            years_of_experience=self._normalize_text(raw_payload.get("years_of_experience")),
            minimum_level_of_studies=self._normalize_text(
                raw_payload.get("minimum_level_of_studies")
            ),
            english_required=self._normalize_english_required(raw_payload.get("english_required")),
            model=str(getattr(response, "model", self.config.model) or self.config.model),
            response_id=self._normalize_optional_text(getattr(response, "id", None)),
            raw_payload=raw_payload,
        )

    def generate_chat_completion(self, messages: list[dict[str, Any]]) -> dict[str, object]:
        """Compatibility wrapper that returns the historical JSON-compatible shape."""
        description = self._extract_description_from_messages(messages)
        return self.extract_job_description(description).to_legacy_dict()

    @staticmethod
    def _normalize_text(value: object) -> str:
        normalized = str(value or "").strip()
        return normalized or NOT_AVAILABLE

    @staticmethod
    def _normalize_optional_text(value: object) -> str | None:
        normalized = str(value or "").strip()
        return normalized or None

    @staticmethod
    def _normalize_english_required(value: object) -> bool | None:
        if isinstance(value, bool):
            return value
        return None

    @staticmethod
    def _extract_description_from_messages(messages: list[dict[str, Any]]) -> str:
        for message in reversed(messages):
            if message.get("role") != "user":
                continue

            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_parts = [part.get("text", "") for part in content if isinstance(part, dict)]
                return "\n".join(part for part in text_parts if part)

        raise ValueError("No user message content found in OpenAI prompt payload.")


__all__ = [
    "OpenAIConfigurationError",
    "OpenAIDependencyError",
    "OpenAIHandler",
    "SYSTEM_PROMPT",
]
