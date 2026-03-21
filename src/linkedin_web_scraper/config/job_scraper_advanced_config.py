from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(slots=True)
class JobScraperAdvancedConfig:
    """Optional advanced configuration overrides for scraping and enrichment."""

    LOCATION_MAPPING: dict[str, str] | None = None
    KEYWORDS: list[str] | None = None
    SKILLS_CATEGORIES: dict[str, list[str]] | None = None

    def __post_init__(self) -> None:
        if self.LOCATION_MAPPING is not None:
            self.LOCATION_MAPPING = dict(self.LOCATION_MAPPING)
        if self.KEYWORDS is not None:
            self.KEYWORDS = list(self.KEYWORDS)
        if self.SKILLS_CATEGORIES is not None:
            self.SKILLS_CATEGORIES = {
                category: list(items) for category, items in self.SKILLS_CATEGORIES.items()
            }

    @classmethod
    def from_collections(
        cls,
        *,
        location_mapping: Mapping[str, str] | None = None,
        keywords: Sequence[str] | None = None,
        skills_categories: Mapping[str, Sequence[str]] | None = None,
    ) -> JobScraperAdvancedConfig:
        """Build a config from generic mapping and sequence inputs."""
        normalized_skills = None
        if skills_categories is not None:
            normalized_skills = {
                category: list(items) for category, items in skills_categories.items()
            }

        return cls(
            LOCATION_MAPPING=dict(location_mapping) if location_mapping is not None else None,
            KEYWORDS=list(keywords) if keywords is not None else None,
            SKILLS_CATEGORIES=normalized_skills,
        )
