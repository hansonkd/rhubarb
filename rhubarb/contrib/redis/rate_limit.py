from contextlib import AsyncContextDecorator

from rhubarb import RhubarbException
from rhubarb.config import config
from rhubarb.contrib.redis.connection import connection


class RateLimitExceeded(RhubarbException):
    pass


class RateLimit(AsyncContextDecorator):
    def __init__(self, key: str, max_times: int, ttl_seconds: int):
        self.original_key = key
        self.key = f"_rl-{key}"
        self.max_times = max_times
        self.ttl_seconds = ttl_seconds

    async def __aenter__(self):
        async with connection() as conn:
            pipeline = conn.pipeline()
            pipeline.incr(self.key)
            pipeline.expire(self.key, self.ttl_seconds, nx=True)
            result = await pipeline.execute()
            times_hit = result[0]
            if times_hit > self.max_times:
                raise RateLimitExceeded(f"Rate limit for {self.original_key} exceeded. {times_hit} > {self.max_times}")
        return self

    async def __aexit__(self, *exc):
        return False


rate_limit = RateLimit
