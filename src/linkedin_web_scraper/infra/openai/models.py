"""Typed models and protocols shared by the optional enrichment adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Protocol, runtime_checkable

from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL

NOT_AVAILABLE = "N/A"

SYSTEM_PROMPT = """You extract structured data from job descriptions. Return a concise English summary of the role itself, list the relevant hard skills and technologies, capture explicit experience requirements when present, capture the minimum level of studies when present, and mark whether English proficiency is required. If the source description is in English, treat English as required. Do not include company marketing or unrelated company background in the summary."""


class EnrichmentDependencyError(RuntimeError):
    """Raised when optional enrichment dependencies are missing."""


@lru_cache(maxsize=1)
def load_response_schema() -> type[Any]:
    """Build the provider-neutral structured-output schema for enrichment."""
    try:
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise EnrichmentDependencyError(
            "Structured enrichment parsing requires the optional dependencies "
            "installed via `.[openai]` or `.[anthropic]`."
        ) from exc

    class JobDescriptionSchema(BaseModel):
        description: str = Field(
            description="A concise English summary of the job responsibilities only."
        )
        tech_stack: list[str] = Field(
            default_factory=list,
            description="Relevant programming languages, tools, frameworks, and hard skills.",
        )
        years_of_experience: str = Field(
            default=NOT_AVAILABLE,
            description="Experience requirement as written in the job description, or N/A.",
        )
        minimum_level_of_studies: str = Field(
            default=NOT_AVAILABLE,
            description="Minimum education requirement, or N/A if not stated.",
        )
        english_required: bool | None = Field(
            default=None,
            description="True when English proficiency is required or clearly implied.",
        )

    return JobDescriptionSchema


@dataclass(slots=True, frozen=True)
class EnrichmentClientConfig:
    """Provider-neutral model and credential settings for an enrichment client."""

    model: str
    api_key: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "model", str(self.model).strip())

        if self.api_key is not None:
            normalized_api_key = self.api_key.strip()
            object.__setattr__(self, "api_key", normalized_api_key or None)


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
