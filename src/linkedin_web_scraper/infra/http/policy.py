from __future__ import annotations

from dataclasses import dataclass, field, replace

from linkedin_web_scraper.config.constants import USER_AGENT_HEADERS

DEFAULT_REQUEST_TIMEOUT = 10.0
DEFAULT_MAX_RETRIES = 5
DEFAULT_INITIAL_BACKOFF = 1.0
DEFAULT_MAX_BACKOFF = 60.0
DEFAULT_RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)


@dataclass(frozen=True, slots=True)
class HttpRequestPolicy:
    """Retry, timeout, and header policy for HTTP scraping requests."""

    timeout: float = DEFAULT_REQUEST_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    initial_backoff: float = DEFAULT_INITIAL_BACKOFF
    max_backoff: float = DEFAULT_MAX_BACKOFF
    retryable_status_codes: tuple[int, ...] = DEFAULT_RETRYABLE_STATUS_CODES
    user_agent_headers: tuple[dict[str, str], ...] = field(
        default_factory=lambda: tuple(dict(header) for header in USER_AGENT_HEADERS)
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "timeout", float(self.timeout))
        object.__setattr__(self, "max_retries", int(self.max_retries))
        object.__setattr__(self, "initial_backoff", float(self.initial_backoff))
        object.__setattr__(self, "max_backoff", float(self.max_backoff))
        object.__setattr__(
            self,
            "retryable_status_codes",
            tuple(int(status_code) for status_code in self.retryable_status_codes),
        )
        object.__setattr__(
            self,
            "user_agent_headers",
            tuple(dict(header) for header in self.user_agent_headers),
        )

        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries <= 0:
            raise ValueError("max_retries must be positive")
        if self.initial_backoff < 0:
            raise ValueError("initial_backoff cannot be negative")
        if self.max_backoff <= 0:
            raise ValueError("max_backoff must be positive")
        if not self.user_agent_headers:
            raise ValueError("user_agent_headers must contain at least one header")

    def with_overrides(
        self,
        *,
        timeout: float | None = None,
        max_retries: int | None = None,
        initial_backoff: float | None = None,
        max_backoff: float | None = None,
        retryable_status_codes: tuple[int, ...] | None = None,
    ) -> HttpRequestPolicy:
        """Return a copy of the policy with selected fields replaced."""
        replacements = {}
        if timeout is not None:
            replacements["timeout"] = timeout
        if max_retries is not None:
            replacements["max_retries"] = max_retries
        if initial_backoff is not None:
            replacements["initial_backoff"] = initial_backoff
        if max_backoff is not None:
            replacements["max_backoff"] = max_backoff
        if retryable_status_codes is not None:
            replacements["retryable_status_codes"] = retryable_status_codes
        return replace(self, **replacements)