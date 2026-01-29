"""Tests for rate limiter."""

import time
import pytest

from argent.tools.rate_limiter import (
    RateLimiter,
    DataSource,
    RATE_LIMITS,
    get_rate_limiter,
)


class TestRateLimiter:
    """Tests for the rate limiter."""

    def test_rate_limits_defined(self):
        """Test that all data sources have rate limits defined."""
        for source in DataSource:
            assert source in RATE_LIMITS

    def test_min_interval_calculation(self):
        """Test minimum interval calculation."""
        # Yahoo Finance: 2 req/sec = 0.5 sec interval
        assert abs(RATE_LIMITS[DataSource.YAHOO_FINANCE].min_interval - 0.5) < 0.01

        # Alpha Vantage: 0.083 req/sec = ~12 sec interval
        assert abs(RATE_LIMITS[DataSource.ALPHA_VANTAGE].min_interval - 12.048) < 0.1

    def test_sync_acquire_timing(self):
        """Test that sync acquire respects rate limits."""
        limiter = RateLimiter()

        # Make two requests to Yahoo Finance
        start = time.monotonic()
        limiter.acquire_sync(DataSource.YAHOO_FINANCE)
        limiter.acquire_sync(DataSource.YAHOO_FINANCE)
        elapsed = time.monotonic() - start

        # Should have waited at least the minimum interval
        min_interval = RATE_LIMITS[DataSource.YAHOO_FINANCE].min_interval
        assert elapsed >= min_interval * 0.9  # Allow 10% tolerance

    def test_different_sources_independent(self):
        """Test that different sources have independent rate limits."""
        limiter = RateLimiter()

        # Make request to Yahoo Finance
        limiter.acquire_sync(DataSource.YAHOO_FINANCE)

        # Should be able to immediately request from FRED
        start = time.monotonic()
        limiter.acquire_sync(DataSource.FRED)
        elapsed = time.monotonic() - start

        # Should be nearly instant (no waiting)
        assert elapsed < 0.1

    def test_global_limiter_singleton(self):
        """Test that get_rate_limiter returns same instance."""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()

        assert limiter1 is limiter2


@pytest.mark.asyncio
class TestAsyncRateLimiter:
    """Async tests for rate limiter."""

    async def test_async_acquire_timing(self):
        """Test that async acquire respects rate limits."""
        limiter = RateLimiter()

        start = time.monotonic()
        await limiter.acquire(DataSource.YAHOO_FINANCE)
        await limiter.acquire(DataSource.YAHOO_FINANCE)
        elapsed = time.monotonic() - start

        min_interval = RATE_LIMITS[DataSource.YAHOO_FINANCE].min_interval
        assert elapsed >= min_interval * 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
