"""Rate limiter and retry utilities for LLM API calls."""

from __future__ import annotations

import asyncio
import logging
import random
import time
from functools import wraps
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimiter:
    def __init__(self, requests_per_minute: float = 60, burst_size: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
        self.refill_rate = requests_per_minute / 60.0

    async def acquire(self) -> None:
        async with self._lock:
            await self._wait_for_token()
            self.tokens -= 1

    async def _wait_for_token(self) -> None:
        while True:
            self._refill_tokens()
            if self.tokens >= 1:
                return
            tokens_needed = 1 - self.tokens
            wait_time = tokens_needed / self.refill_rate
            wait_time += random.uniform(0, 0.1)
            logger.debug(f"Rate limiter waiting {wait_time:.2f}s for token")
            await asyncio.sleep(wait_time)

    def _refill_tokens(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_update
        self.last_update = now
        self.tokens = min(self.burst_size, self.tokens + elapsed * self.refill_rate)


class RetryConfig:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (Exception,)


RATE_LIMIT_PATTERNS = [
    "rate limit",
    "rate_limit",
    "too many requests",
    "quota exceeded",
    "resource exhausted",
    "429",
    "503",
    "overloaded",
]


def is_retryable_error(error: Exception) -> bool:
    error_str = str(error).lower()

    if hasattr(error, "__class__"):
        class_name = error.__class__.__name__
        if "RateLimit" in class_name or "rate_limit" in class_name:
            return True
        if "APIConnectionError" in class_name or "APITimeoutError" in class_name:
            return True
        if "InternalServerError" in class_name or "ServiceUnavailable" in class_name:
            return True
        if "ConnectionError" in class_name or "TimeoutError" in class_name:
            return True

    for pattern in RATE_LIMIT_PATTERNS:
        if pattern in error_str:
            return True

    if hasattr(error, "status_code") and error.status_code in (429, 500, 502, 503, 504):
        return True

    if hasattr(error, "response") and hasattr(error.response, "status_code"):
        if error.response.status_code in (429, 500, 502, 503, 504):
            return True

    if hasattr(error, "code"):
        error_code = str(error.code).lower()
        retryable_codes = [
            "rate_limit_exceeded",
            "server_error",
            "timeout",
            "internal_error",
            "service_unavailable",
        ]
        if any(code in error_code for code in retryable_codes):
            return True

    if hasattr(error, "body"):
        body_str = str(error.body).lower()
        for pattern in RATE_LIMIT_PATTERNS:
            if pattern in body_str:
                return True

    return False


async def retry_with_backoff(
    func: Callable[..., T],
    config: RetryConfig = None,
    *args,
    **kwargs,
) -> T:
    config = config or RetryConfig()
    last_exception = None

    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if not is_retryable_error(e):
                logger.warning(f"Non-retryable error: {e}")
                raise

            if config.retryable_exceptions and config.retryable_exceptions != (Exception,):
                if not isinstance(e, config.retryable_exceptions):
                    logger.warning(
                        f"Error type {type(e).__name__} not in retryable_exceptions, not retrying"
                    )
                    raise

            if attempt == config.max_retries:
                logger.error(f"Max retries ({config.max_retries}) exceeded: {e}")
                raise

            delay = min(
                config.base_delay * (config.exponential_base**attempt),
                config.max_delay,
            )
            if config.jitter:
                delay *= 0.5 + random.random()

            logger.warning(
                f"Retry {attempt + 1}/{config.max_retries} after {delay:.2f}s due to: {e}"
            )
            await asyncio.sleep(delay)

    if last_exception:
        raise last_exception
    raise RuntimeError("Retry loop completed without result or exception")


def with_rate_limit_and_retry(
    rate_limiter: RateLimiter = None,
    retry_config: RetryConfig = None,
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if rate_limiter:
                await rate_limiter.acquire()
            if retry_config:
                return await retry_with_backoff(func, retry_config, *args, **kwargs)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


_default_rate_limiter: RateLimiter | None = None
_default_retry_config: RetryConfig | None = None


def get_default_rate_limiter() -> RateLimiter:
    global _default_rate_limiter
    if _default_rate_limiter is None:
        _default_rate_limiter = RateLimiter(requests_per_minute=60, burst_size=10)
    return _default_rate_limiter


def get_default_retry_config() -> RetryConfig:
    global _default_retry_config
    if _default_retry_config is None:
        _default_retry_config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0,
            jitter=True,
        )
    return _default_retry_config


def configure_rate_limiter(
    requests_per_minute: float = 60,
    burst_size: int = 10,
) -> RateLimiter:
    global _default_rate_limiter
    _default_rate_limiter = RateLimiter(
        requests_per_minute=requests_per_minute,
        burst_size=burst_size,
    )
    return _default_rate_limiter


def configure_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> RetryConfig:
    global _default_retry_config
    _default_retry_config = RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
    )
    return _default_retry_config
