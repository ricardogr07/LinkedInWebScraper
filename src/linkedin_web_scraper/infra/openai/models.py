"""Typed models and protocols for optional OpenAI enrichment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL

NOT_AVAILABLE = "N/A"


@dataclass(slots=True, frozen=True)
class OpenAIEnrichmentConfig:
    """Runtime configuration for OpenAI-backed enrichment."""

    model: str = DEFAULT_OPENAI_MODEL
    api_key: str | None = None

    def __post_init__(self) -> None:
        normalized_model = (self.model or DEFAULT_OPENAI_MODEL).strip()
        object.__setattr__(self, "model", normalized_model or DEFAULT_OPENAI_MODEL)

        if self.api_key is not None:
            normalized_api_key = self.api_key.strip()
            object.__setattr__(self, "api_key", normalized_api_key or None)


@dataclass(slots=True, frozen=True)
class JobDescriptionEnrichment:
    """Structured job-description enrichment output."""

    short_description: str = NOT_AVAILABLE
    tech_stack: tuple[str, ...] = ()
    years_of_experience: str = NOT_AVAILABLE
    minimum_level_of_studies: str = NOT_AVAILABLE
    english_required: bool | None = None
    model: str | None = None
    response_id: str | None = None
    raw_payload: dict[str, object] = field(default_factory=dict)

    @property
    def tech_stack_text(self) -> str:
        """Return the tech stack as a comma-separated string for dataframe storage."""
        return ", ".join(self.tech_stack) if self.tech_stack else NOT_AVAILABLE

    @property
    def english_requirement_text(self) -> bool | str:
        """Return a dataframe-friendly English requirement value."""
        if self.english_required is None:
            return NOT_AVAILABLE
        return self.english_required

    def to_legacy_dict(self) -> dict[str, object]:
        """Convert the structured result into the legacy JSON-compatible shape."""
        return {
            "Description": self.short_description,
            "TechStack": list(self.tech_stack),
            "YoE": self.years_of_experience,
            "MinLevelStudies": self.minimum_level_of_studies,
            "English": self.english_requirement_text,
        }


@runtime_checkable
class JobDescriptionEnricher(Protocol):
    """Protocol for adapters that can enrich a raw job description."""

    def extract_job_description(self, description: str) -> JobDescriptionEnrichment:
        """Return a structured enrichment result for a single job description."""


__all__ = [
    "JobDescriptionEnrichment",
    "JobDescriptionEnricher",
    "NOT_AVAILABLE",
    "OpenAIEnrichmentConfig",
]
