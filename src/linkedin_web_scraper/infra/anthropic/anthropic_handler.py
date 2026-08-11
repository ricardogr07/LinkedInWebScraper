"""Optional Anthropic adapter built on the Messages structured-output API."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

from linkedin_web_scraper.config.anthropic import DEFAULT_ANTHROPIC_MODEL
from linkedin_web_scraper.infra.logging import Logger, resolve_logger
from linkedin_web_scraper.infra.openai.models import (
    NOT_AVAILABLE,
    SYSTEM_PROMPT,
    EnrichmentDependencyError,
    JobDescriptionEnrichment,
    load_response_schema,
)

DEFAULT_ANTHROPIC_MAX_TOKENS = 1024


class AnthropicConfigurationError(RuntimeError):
    """Raised when Anthropic enrichment is requested without valid configuration."""


class AnthropicDependencyError(EnrichmentDependencyError):
    """Raised when optional Anthropic enrichment dependencies are missing."""


@lru_cache(maxsize=1)
def _load_anthropic_client_class() -> type[Any]:
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise AnthropicDependencyError(
            "Anthropic enrichment requires the optional dependencies installed via `.[anthropic]`."
        ) from exc
    return Anthropic


class AnthropicHandler:
    """Handle optional Anthropic job-description enrichment using structured parsing."""

    def __init__(
        self,
        logger: logging.Logger | Logger | None = None,
        *,
        model: str = DEFAULT_ANTHROPIC_MODEL,
        api_key: str | None = None,
        client: Any | None = None,
    ):
        self.logger = resolve_logger(logger, name=__name__)
        self.model = str(model).strip() or DEFAULT_ANTHROPIC_MODEL
        self.api_key = api_key.strip() if api_key else None
        self.client = client or self._configure_anthropic()

    def _configure_anthropic(self) -> Any:
        """Create an Anthropic client from the explicit config or environment variables."""
        api_key = self._resolve_api_key()
        client_class = _load_anthropic_client_class()
        self.logger.info("Configuring Anthropic client for model %s.", self.model)
        return client_class(api_key=api_key)

    def _resolve_api_key(self) -> str:
        """Resolve the Anthropic API key from the handler config or environment."""
        if self.api_key is not None:
            return self.api_key

        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not anthropic_api_key:
            raise AnthropicConfigurationError(
                "Anthropic enrichment requires `ANTHROPIC_API_KEY` in the environment "
                "or an injected client."
            )
        return anthropic_api_key

    def extract_job_description(self, description: str) -> JobDescriptionEnrichment:
        """Return structured enrichment data for a single job description."""
        normalized_description = str(description).strip()
        if not normalized_description:
            return JobDescriptionEnrichment()

        response = self.client.messages.parse(
            model=self.model,
            max_tokens=DEFAULT_ANTHROPIC_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": normalized_description}],
            output_format=load_response_schema(),
        )
        parsed = getattr(response, "parsed_output", None)
        if parsed is None:
            raise RuntimeError("Anthropic response did not include a parsed structured payload.")

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
            model=str(getattr(response, "model", self.model) or self.model),
            response_id=self._normalize_optional_text(getattr(response, "id", None)),
            raw_payload=raw_payload,
        )

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


__all__ = [
    "AnthropicConfigurationError",
    "AnthropicDependencyError",
    "AnthropicHandler",
]
