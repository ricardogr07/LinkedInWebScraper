from __future__ import annotations

import sys

from linkedin_web_scraper.interfaces.cli.main import main as cli_main


def main(argv: list[str] | None = None) -> int:
    """Run the legacy root daily entrypoint via the package CLI."""
    return cli_main(list(argv) if argv is not None else ["scrape", "daily"])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or ["scrape", "daily"]))
