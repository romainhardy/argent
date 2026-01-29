"""Rate limiter for API calls to respect free tier limits."""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class DataSource(str, Enum):
    """Supported data sources with their rate limits."""

    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    FRED = "fred"
    COINGECKO = "coingecko"


@dataclass
class RateLimitConfig:
    """Rate limit configuration for a data source."""

    requests_per_second: float
    burst_limit: int = 1

    @property
    def min_interval(self) -> float:
        """Minimum interval between requests in seconds."""
        return 1.0 / self.requests_per_second


# Free tier rate limits
RATE_LIMITS: dict[DataSource, RateLimitConfig] = {
    DataSource.YAHOO_FINANCE: RateLimitConfig(requests_per_second=2.0, burst_limit=5),
    DataSource.ALPHA_VANTAGE: RateLimitConfig(requests_per_second=0.083, burst_limit=1),  # 5/min
    DataSource.FRED: RateLimitConfig(requests_per_second=1.0, burst_limit=10),
    DataSource.COINGECKO: RateLimitConfig(requests_per_second=0.1, burst_limit=3),  # 10-30/min
}


@dataclass
class RateLimiter:
    """Thread-safe rate limiter for multiple data sources."""

    _last_request: dict[DataSource, float] = field(default_factory=lambda: defaultdict(float))
    _locks: dict[DataSource, asyncio.Lock] = field(
        default_factory=lambda: defaultdict(asyncio.Lock)
    )

    async def acquire(self, source: DataSource) -> None:
        """Wait until a request can be made to the given source."""
        config = RATE_LIMITS.get(source)
        if not config:
            return

        async with self._locks[source]:
            now = time.monotonic()
            elapsed = now - self._last_request[source]
            wait_time = config.min_interval - elapsed

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            self._last_request[source] = time.monotonic()

    def acquire_sync(self, source: DataSource) -> None:
        """Synchronous version of acquire for non-async contexts."""
        config = RATE_LIMITS.get(source)
        if not config:
            return

        now = time.monotonic()
        elapsed = now - self._last_request[source]
        wait_time = config.min_interval - elapsed

        if wait_time > 0:
            time.sleep(wait_time)

        self._last_request[source] = time.monotonic()


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
