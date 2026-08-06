"""Command-line entrypoints for runtime-configured scrape workflows."""

from __future__ import annotations

import argparse
import sys
from typing import TextIO

from linkedin_web_scraper.application.runtime_runner import RuntimeRunner
from linkedin_web_scraper.config.runtime import RuntimeConfig, load_runtime_config
from linkedin_web_scraper.infra.logging import configure_logging, get_logger


def build_parser() -> argparse.ArgumentParser:
    """Build the package CLI argument parser."""
    parser = argparse.ArgumentParser(prog="linkedin-webscraper")
    parser.add_argument("--config", dest="config_path", help="Path to a runtime TOML config file.")

    subparsers = parser.add_subparsers(dest="command")
    common_parent = argparse.ArgumentParser(add_help=False)
    common_parent.add_argument("--config", dest="config_path")
    common_parent.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved runtime plan without running it.",
    )

    scrape_parser = subparsers.add_parser("scrape", help="Run scrape workflows.")
    scrape_subparsers = scrape_parser.add_subparsers(dest="scrape_command")

    once_parser = scrape_subparsers.add_parser(
        "once",
        parents=[common_parent],
        help="Run a single-location scrape and persist/export the result.",
    )
    once_parser.add_argument("--position")
    once_parser.add_argument("--location")
    once_parser.add_argument("--time-posted")
    once_parser.add_argument("--remote-types", nargs="+")
    once_parser.add_argument("--file-name")
    once_parser.add_argument("--output-dir")
    once_parser.add_argument("--openai-model")
    once_openai_group = once_parser.add_mutually_exclusive_group()
    once_openai_group.add_argument("--openai-enabled", dest="openai_enabled", action="store_true")
    once_openai_group.add_argument("--openai-disabled", dest="openai_enabled", action="store_false")
    once_parser.set_defaults(openai_enabled=None)
    once_append_group = once_parser.add_mutually_exclusive_group()
    once_append_group.add_argument("--append", dest="append", action="store_true")
    once_append_group.add_argument("--no-append", dest="append", action="store_false")
    once_parser.set_defaults(append=None)

    daily_parser = scrape_subparsers.add_parser(
        "daily",
        parents=[common_parent],
        help="Run the daily multi-city scrape and persist/export the results.",
    )
    daily_parser.add_argument("--cities", nargs="+")
    daily_parser.add_argument("--position")
    daily_parser.add_argument("--time-posted")
    daily_parser.add_argument("--combined-file-name")
    daily_parser.add_argument("--output-dir")
    daily_parser.add_argument("--openai-model")
    daily_openai_group = daily_parser.add_mutually_exclusive_group()
    daily_openai_group.add_argument("--openai-enabled", dest="openai_enabled", action="store_true")
    daily_openai_group.add_argument(
        "--openai-disabled", dest="openai_enabled", action="store_false"
    )
    daily_parser.set_defaults(openai_enabled=None)

    export_parser = subparsers.add_parser(
        "export",
        parents=[common_parent],
        help="Export one persisted scrape run from SQLite to CSV.",
    )
    export_parser.add_argument("--run-id")
    export_parser.add_argument("--file-name")
    export_parser.add_argument("--output-dir")

    return parser


def _format_plan(plan: dict[str, object]) -> str:
    lines = ["Dry run plan:"]
    for key, value in plan.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def _apply_once_overrides(runtime_config: RuntimeConfig, args: argparse.Namespace) -> None:
    config = runtime_config.scrape_once
    if getattr(args, "position", None):
        config.position = args.position
    if getattr(args, "location", None):
        config.location = args.location
    if getattr(args, "time_posted", None):
        config.time_posted = args.time_posted
    if getattr(args, "remote_types", None):
        config.remote_types = tuple(args.remote_types)
    if getattr(args, "file_name", None):
        config.file_name = args.file_name
    if getattr(args, "output_dir", None):
        config.output_dir = args.output_dir
    if getattr(args, "openai_model", None):
        config.openai_model = args.openai_model
    if getattr(args, "openai_enabled", None) is not None:
        config.openai_enabled = args.openai_enabled
    if getattr(args, "append", None) is not None:
        config.append = args.append
    config.__post_init__()


def _apply_daily_overrides(runtime_config: RuntimeConfig, args: argparse.Namespace) -> None:
    config = runtime_config.scrape_daily
    if getattr(args, "cities", None):
        config.cities = tuple(args.cities)
    if getattr(args, "position", None):
        config.position = args.position
    if getattr(args, "time_posted", None):
        config.time_posted = args.time_posted
    if getattr(args, "combined_file_name", None):
        config.combined_file_name = args.combined_file_name
    if getattr(args, "output_dir", None):
        config.output_dir = args.output_dir
    if getattr(args, "openai_model", None):
        config.openai_model = args.openai_model
    if getattr(args, "openai_enabled", None) is not None:
        config.openai_enabled = args.openai_enabled
    config.__post_init__()


def _apply_export_overrides(runtime_config: RuntimeConfig, args: argparse.Namespace) -> None:
    config = runtime_config.export
    if getattr(args, "run_id", None):
        config.run_id = args.run_id
    if getattr(args, "file_name", None):
        config.file_name = args.file_name
    if getattr(args, "output_dir", None):
        config.output_dir = args.output_dir
    config.__post_init__()


def _resolve_command(args: argparse.Namespace) -> tuple[str, str | None]:
    if args.command is None:
        return ("scrape", "daily")
    return (args.command, getattr(args, "scrape_command", None))


def main(
    argv: list[str] | None = None,
    *,
    runner_cls=RuntimeRunner,
    configure_logging_fn=configure_logging,
    logger_factory=get_logger,
    stdout: TextIO | None = None,
) -> int:
    """Run the package CLI with runtime-configured scrape workflows."""
    output = stdout or sys.stdout
    parser = build_parser()
    parsed_args = parser.parse_args(argv)
    command, scrape_command = _resolve_command(parsed_args)

    runtime_config = load_runtime_config(parsed_args.config_path)
    configure_logging_fn(
        filename=runtime_config.logging.file_name,
        level=runtime_config.logging.level,
    )
    runner = runner_cls(logger=logger_factory(__name__))

    if command == "scrape" and scrape_command in (None, "daily"):
        _apply_daily_overrides(runtime_config, parsed_args)
        if getattr(parsed_args, "dry_run", False):
            print(_format_plan(runner.describe_daily(runtime_config)), file=output)
            return 0
        runner.run_daily(runtime_config)
        return 0

    if command == "scrape" and scrape_command == "once":
        _apply_once_overrides(runtime_config, parsed_args)
        if getattr(parsed_args, "dry_run", False):
            print(_format_plan(runner.describe_once(runtime_config)), file=output)
            return 0
        runner.run_once(runtime_config)
        return 0

    if command == "export":
        _apply_export_overrides(runtime_config, parsed_args)
        if getattr(parsed_args, "dry_run", False):
            print(_format_plan(runner.describe_export(runtime_config)), file=output)
            return 0
        runner.export_run(runtime_config)
        return 0

    parser.error("A valid command is required.")
    return 2


__all__ = ["build_parser", "main"]
