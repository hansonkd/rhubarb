import asyncio
import dataclasses
from urllib.parse import urlparse

from psycopg_pool import AsyncConnectionPool

from rhubarb.env import str_env, int_env
from .connection_base import AsyncConnectionWithStats


pools = {}
pool_lock = asyncio.Lock()


@dataclasses.dataclass(frozen=True)
class PostgresConfig:
    host: str = str_env("PG_HOST", "localhost")
    port: int = int_env("PG_PORT", 5432)
    user: str = str_env("PG_USER", "postgres")
    password: str = str_env("PG_PASSWORD", "postgres")
    dbname: str = str_env("PG_DBNAME", "postgres")
    min_size: int = int_env("PG_POOL_MIN_SIZE", 4)
    max_size: int | None = int_env("PG_POOL_MAX_SIZE")

    async def get_pool(self) -> AsyncConnectionPool:
        if self in pools:
            return pools[self]
        async with pool_lock:
            kwargs = dataclasses.asdict(self)
            min_size = kwargs.pop("min_size")
            max_size = kwargs.pop("max_size")
            pool = AsyncConnectionPool(
                connection_class=AsyncConnectionWithStats, kwargs=kwargs, min_size=min_size, max_size=max_size
            )
            await pool.open(wait=True, timeout=10)
            pools[self] = pool
            return pool


DEFAULT_URI_ENV = "PG_DATABASE_URI"


def load_postgres_config(extra_env_key=None):
    if db_url := (extra_env_key and str_env(extra_env_key)) or str_env(DEFAULT_URI_ENV):
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        return PostgresConfig(
            host=str(hostname),
            port=int(port),
            user=str(username),
            dbname=str(database),
            password=str(password),
        )
    return PostgresConfig()
