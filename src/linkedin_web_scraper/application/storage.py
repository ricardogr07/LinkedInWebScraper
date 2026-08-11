"""Application-layer storage contracts for persisted scrape runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import pandas as pd


@dataclass(slots=True)
class ScrapeRunContext:
    """Describe one persisted scrape run at the application boundary."""

    position: str
    location: str
    enrichment_provider: str
    time_posted: str
    remote_types: tuple[str, ...] = ()
    output_path: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.position = self.position.strip()
        self.location = self.location.strip()
        self.enrichment_provider = str(self.enrichment_provider).strip().upper()
        self.time_posted = str(self.time_posted).strip().upper()
        self.remote_types = tuple(str(remote).strip() for remote in self.remote_types)
        self.metadata = dict(self.metadata)


@runtime_checkable
class ScrapeStorage(Protocol):
    """Protocol for run-scoped scrape persistence implementations."""

    def begin_run(self, context: ScrapeRunContext) -> str:
        """Create and return a persisted run identifier."""

    def store_jobs(self, run_id: str, df_jobs: pd.DataFrame) -> None:
        """Persist the dataframe for a previously created scrape run."""

    def load_run_jobs(self, run_id: str) -> pd.DataFrame:
        """Load the persisted dataframe for one scrape run."""

    def finish_run(
        self,
        run_id: str,
        *,
        status: str = "completed",
        output_path: str | None = None,
        error_message: str | None = None,
        row_count: int | None = None,
    ) -> None:
        """Mark the scrape run as finished and optionally attach result metadata."""


__all__ = ["ScrapeRunContext", "ScrapeStorage"]
