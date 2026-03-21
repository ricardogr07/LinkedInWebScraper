"""Runtime configuration models and TOML loading helpers for CLI workflows."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from linkedin_web_scraper.config.openai import DEFAULT_OPENAI_MODEL
from linkedin_web_scraper.config.options import RemoteType, TimePosted
from linkedin_web_scraper.config.storage import DEFAULT_SQLITE_DB_FILE

DEFAULT_RUNTIME_CONFIG_FILE = Path("runtime.toml")
DEFAULT_RUNTIME_CITIES: tuple[str, ...] = ("Monterrey", "Guadalajara", "Mexico City")
DEFAULT_RUNTIME_REMOTE_TYPES: tuple[RemoteType, ...] = (
    RemoteType.REMOTE,
    RemoteType.HYBRID,
    RemoteType.ON_SITE,
)


def _normalize_string(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _normalize_bool(value: bool | str) -> bool:
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value}")


def _normalize_time_posted(value: str | TimePosted) -> TimePosted:
    if isinstance(value, TimePosted):
        return value
    return TimePosted(str(value).strip().upper())


def _normalize_remote_type(value: str | RemoteType) -> RemoteType:
    if isinstance(value, RemoteType):
        return value
    normalized = str(value).strip().upper().replace("_", "-")
    return RemoteType(normalized)


def _normalize_remote_types(
    values: Sequence[str | RemoteType] | None,
) -> tuple[RemoteType, ...]:
    if values is None:
        return DEFAULT_RUNTIME_REMOTE_TYPES
    return tuple(_normalize_remote_type(value) for value in values)


@dataclass(slots=True)
class LoggingRuntimeConfig:
    """Runtime logging settings for CLI and script entrypoints."""

    level: str = "INFO"
    file_name: str = "main.log"

    def __post_init__(self) -> None:
        self.level = str(self.level).strip().upper()
        self.file_name = str(self.file_name).strip() or "main.log"


@dataclass(slots=True)
class StorageRuntimeConfig:
    """Runtime storage settings for persisted scrape runs."""

    url: str | None = None
    file_name: str = DEFAULT_SQLITE_DB_FILE
    state_dir: str | None = None

    def __post_init__(self) -> None:
        self.url = _normalize_string(self.url)
        self.file_name = str(self.file_name).strip() or DEFAULT_SQLITE_DB_FILE
        self.state_dir = _normalize_string(self.state_dir)


@dataclass(slots=True)
class ScrapeOnceRuntimeConfig:
    """Runtime defaults for a single-location scrape command."""

    position: str = "Data Scientist"
    location: str = "Monterrey"
    openai_enabled: bool = False
    openai_model: str = DEFAULT_OPENAI_MODEL
    time_posted: TimePosted = TimePosted.DAY
    remote_types: tuple[RemoteType, ...] = DEFAULT_RUNTIME_REMOTE_TYPES
    file_name: str | None = None
    output_dir: str | None = None
    append: bool = True

    def __post_init__(self) -> None:
        self.position = str(self.position).strip()
        self.location = str(self.location).strip()
        self.openai_enabled = _normalize_bool(self.openai_enabled)
        self.openai_model = str(self.openai_model).strip() or DEFAULT_OPENAI_MODEL
        self.time_posted = _normalize_time_posted(self.time_posted)
        self.remote_types = _normalize_remote_types(self.remote_types)
        self.file_name = _normalize_string(self.file_name)
        self.output_dir = _normalize_string(self.output_dir)
        self.append = _normalize_bool(self.append)


@dataclass(slots=True)
class ScrapeDailyRuntimeConfig:
    """Runtime defaults for the multi-city daily scrape command."""

    cities: tuple[str, ...] = DEFAULT_RUNTIME_CITIES
    position: str = "Data Scientist"
    openai_enabled: bool = False
    openai_model: str = DEFAULT_OPENAI_MODEL
    time_posted: TimePosted = TimePosted.DAY
    output_dir: str | None = None
    combined_file_name: str | None = None

    def __post_init__(self) -> None:
        self.cities = tuple(str(city).strip() for city in self.cities if str(city).strip())
        self.position = str(self.position).strip()
        self.openai_enabled = _normalize_bool(self.openai_enabled)
        self.openai_model = str(self.openai_model).strip() or DEFAULT_OPENAI_MODEL
        self.time_posted = _normalize_time_posted(self.time_posted)
        self.output_dir = _normalize_string(self.output_dir)
        self.combined_file_name = _normalize_string(self.combined_file_name)


@dataclass(slots=True)
class ExportRuntimeConfig:
    """Runtime defaults for exporting persisted run data to CSV."""

    run_id: str | None = None
    file_name: str = "linkedin_jobs_export.csv"
    output_dir: str | None = None

    def __post_init__(self) -> None:
        self.run_id = _normalize_string(self.run_id)
        self.file_name = str(self.file_name).strip() or "linkedin_jobs_export.csv"
        self.output_dir = _normalize_string(self.output_dir)


@dataclass(slots=True)
class RuntimeConfig:
    """Top-level runtime configuration for CLI and scheduled runs."""

    logging: LoggingRuntimeConfig = field(default_factory=LoggingRuntimeConfig)
    storage: StorageRuntimeConfig = field(default_factory=StorageRuntimeConfig)
    scrape_once: ScrapeOnceRuntimeConfig = field(default_factory=ScrapeOnceRuntimeConfig)
    scrape_daily: ScrapeDailyRuntimeConfig = field(default_factory=ScrapeDailyRuntimeConfig)
    export: ExportRuntimeConfig = field(default_factory=ExportRuntimeConfig)


def _coerce_mapping(value: object, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError(f"Expected mapping for {label}, got {type(value)!r}")
    return {str(key): inner_value for key, inner_value in value.items()}


def runtime_config_from_mapping(data: Mapping[str, Any]) -> RuntimeConfig:
    """Build a runtime config object from TOML-compatible nested mappings."""
    logging_data = _coerce_mapping(data.get("logging"), "logging")
    storage_data = _coerce_mapping(data.get("storage"), "storage")
    scrape_data = _coerce_mapping(data.get("scrape"), "scrape")
    scrape_once_data = _coerce_mapping(scrape_data.get("once"), "scrape.once")
    scrape_daily_data = _coerce_mapping(scrape_data.get("daily"), "scrape.daily")
    export_data = _coerce_mapping(data.get("export"), "export")

    return RuntimeConfig(
        logging=LoggingRuntimeConfig(**logging_data),
        storage=StorageRuntimeConfig(**storage_data),
        scrape_once=ScrapeOnceRuntimeConfig(**scrape_once_data),
        scrape_daily=ScrapeDailyRuntimeConfig(**scrape_daily_data),
        export=ExportRuntimeConfig(**export_data),
    )


def apply_environment_overrides(
    config: RuntimeConfig,
    environ: Mapping[str, str] | None = None,
) -> RuntimeConfig:
    """Apply lightweight environment overrides on top of a loaded runtime config."""
    environment = dict(os.environ if environ is None else environ)

    log_level = environment.get("LINKEDIN_WEB_SCRAPER_LOG_LEVEL")
    if log_level:
        config.logging.level = str(log_level).strip().upper()

    log_file = environment.get("LINKEDIN_WEB_SCRAPER_LOG_FILE")
    if log_file:
        config.logging.file_name = str(log_file).strip()

    storage_url = environment.get("LINKEDIN_WEB_SCRAPER_STORAGE_URL")
    if storage_url:
        config.storage.url = str(storage_url).strip()

    storage_file = environment.get("LINKEDIN_WEB_SCRAPER_STORAGE_FILE")
    if storage_file:
        config.storage.file_name = str(storage_file).strip()

    state_dir = environment.get("LINKEDIN_WEB_SCRAPER_STATE_DIR")
    if state_dir:
        config.storage.state_dir = str(state_dir).strip()

    output_dir = environment.get("LINKEDIN_WEB_SCRAPER_OUTPUT_DIR")
    if output_dir:
        normalized_output_dir = str(output_dir).strip()
        config.scrape_once.output_dir = normalized_output_dir
        config.scrape_daily.output_dir = normalized_output_dir
        config.export.output_dir = normalized_output_dir

    openai_enabled = environment.get("LINKEDIN_WEB_SCRAPER_OPENAI_ENABLED")
    if openai_enabled is not None:
        normalized_openai_enabled = _normalize_bool(openai_enabled)
        config.scrape_once.openai_enabled = normalized_openai_enabled
        config.scrape_daily.openai_enabled = normalized_openai_enabled

    openai_model = environment.get("LINKEDIN_WEB_SCRAPER_OPENAI_MODEL")
    if openai_model:
        normalized_openai_model = str(openai_model).strip()
        config.scrape_once.openai_model = normalized_openai_model
        config.scrape_daily.openai_model = normalized_openai_model

    return config


def resolve_runtime_config_path(
    path: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> Path | None:
    """Resolve the runtime config path from an explicit value or environment."""
    if path is not None:
        return Path(path)

    environment = dict(os.environ if environ is None else environ)
    env_path = environment.get("LINKEDIN_WEB_SCRAPER_CONFIG")
    if env_path:
        return Path(env_path)

    if DEFAULT_RUNTIME_CONFIG_FILE.exists():
        return DEFAULT_RUNTIME_CONFIG_FILE
    return None


def load_runtime_config(
    path: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> RuntimeConfig:
    """Load runtime config from TOML and apply supported environment overrides."""
    resolved_path = resolve_runtime_config_path(path, environ=environ)

    if resolved_path is None:
        return apply_environment_overrides(RuntimeConfig(), environ=environ)

    raw_data = tomllib.loads(resolved_path.read_text(encoding="utf-8"))
    config = runtime_config_from_mapping(raw_data)
    return apply_environment_overrides(config, environ=environ)


__all__ = [
    "DEFAULT_RUNTIME_CITIES",
    "DEFAULT_RUNTIME_CONFIG_FILE",
    "DEFAULT_RUNTIME_REMOTE_TYPES",
    "ExportRuntimeConfig",
    "LoggingRuntimeConfig",
    "RuntimeConfig",
    "ScrapeDailyRuntimeConfig",
    "ScrapeOnceRuntimeConfig",
    "StorageRuntimeConfig",
    "apply_environment_overrides",
    "load_runtime_config",
    "resolve_runtime_config_path",
    "runtime_config_from_mapping",
]
