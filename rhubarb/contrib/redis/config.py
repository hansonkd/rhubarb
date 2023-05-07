import dataclasses
from typing import Optional
from urllib.parse import urlparse

import redis.asyncio as redis

from rhubarb.env import str_env, int_env

pools = {}


@dataclasses.dataclass(frozen=True)
class RedisConfig:
    host: str = str_env("REDIS_HOST", "localhost")
    port: int = int_env("REDIS_PORT", 5432)
    user: str = str_env("REDIS_USER", "postgres")
    password: str = str_env("REDIS_PASSWORD", "postgres")
    db: int = int_env("REDIS_DB", 0)
    max_connections: Optional[int] = int_env("REDIS_MAX_CONNECTIONS")

    async def get_pool(self) -> redis.Redis:
        kwargs = dataclasses.asdict(self)
        redis.ConnectionPool(**kwargs)
        if self in pools:
            return pools[self]
        kwargs = dataclasses.asdict(self)
        pool = redis.ConnectionPool(**kwargs)
        reds_conn = redis.Redis(connection_pool=pool)
        pools[self] = reds_conn
        return reds_conn


DEFAULT_URI_ENV = "REDIS_URI"


def load_redis_config(extra_env_key: str=None):
    if db_url := (extra_env_key and str_env(extra_env_key)) or str_env(DEFAULT_URI_ENV):
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        return RedisConfig(
            host=str(hostname),
            port=int(port),
            user=str(username),
            db=int(database),
            password=str(password),
        )
    return RedisConfig()
