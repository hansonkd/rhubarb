import dataclasses
from typing import Optional
from urllib.parse import urlparse

import redis.asyncio as redis

from rhubarb.env import str_env, int_env

pools = {}


@dataclasses.dataclass(frozen=True)
class RedisConfig:
    host: str = str_env("REDIS_HOST", "127.0.0.1")
    port: int = int_env("REDIS_PORT", 6379)
    password: Optional[str] = str_env("REDIS_PASSWORD", None)
    db: int = int_env("REDIS_DB", 0)
    max_connections: Optional[int] = int_env("REDIS_MAX_CONNECTIONS")

    def get_pool(self) -> redis.ConnectionPool:
        kwargs = dataclasses.asdict(self)
        redis.ConnectionPool(**kwargs)
        if self in pools:
            return pools[self]
        kwargs = dataclasses.asdict(self)
        pool = redis.ConnectionPool(**kwargs)
        pools[self] = pool
        return pool


DEFAULT_URI_ENV = "REDIS_URI"


def load_redis_config(extra_env_key: str = None):
    if db_url := (extra_env_key and str_env(extra_env_key)) or str_env(DEFAULT_URI_ENV):
        result = urlparse(db_url)
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        return RedisConfig(
            host=str(hostname),
            port=int(port),
            db=int(database),
            password=str(password),
        )
    return RedisConfig()
