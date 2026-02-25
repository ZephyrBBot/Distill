import asyncio
import unittest

from core.rate_limiter import RateLimiter as CoreRateLimiter
from distill_lib.rate_limiter import RateLimiter, is_retryable_error, retry_with_backoff


class RateLimiterMigrationTest(unittest.TestCase):
    def test_core_rate_limiter_aliases_distill_lib(self):
        self.assertIs(CoreRateLimiter, RateLimiter)

    def test_is_retryable_error_by_message(self):
        err = RuntimeError("429: too many requests")
        self.assertTrue(is_retryable_error(err))

    def test_retry_with_backoff_retries_then_succeeds(self):
        attempts = {"n": 0}

        async def flaky():
            attempts["n"] += 1
            if attempts["n"] < 2:
                raise RuntimeError("rate limit")
            return "ok"

        result = asyncio.run(retry_with_backoff(flaky))

        self.assertEqual(result, "ok")
        self.assertEqual(attempts["n"], 2)


if __name__ == "__main__":
    unittest.main()
