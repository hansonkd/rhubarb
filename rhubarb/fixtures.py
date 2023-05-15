import dataclasses
from contextlib import contextmanager
from typing import ContextManager, Callable

import pytest
import pytest_asyncio
from psycopg import AsyncConnection

from rhubarb.pkg.postgres.connection import connection
from rhubarb.config import _program_state, Config, PostgresConfig
from rhubarb.pkg.redis.config import pools as redis_pools
from rhubarb.pkg.postgres.config import pools as postgres_pools


@pytest_asyncio.fixture()
async def rhubarb(config_override):
    with config_override(
        Config(
            postgres=PostgresConfig(
            )
        )
    ):
        yield
        for cache in redis_pools.values():
            await cache.disconnect(inuse_connections=True)
        redis_pools.clear()
        for pg_pool in postgres_pools.values():
            await pg_pool.close()
        postgres_pools.clear()


@pytest.fixture(scope="session")
def config_override() -> Callable[[Config], ContextManager]:
    @contextmanager
    def override_config(config: Config):
        old_config = _program_state.config
        _program_state.config = config
        try:
            yield
        finally:
            _program_state.config = old_config

    return override_config


@pytest.fixture(scope="session")
def patch_config() -> Callable[..., ContextManager]:
    @contextmanager
    def override_config(**kwargs):
        old_config = _program_state.config
        _program_state.config = dataclasses.replace(old_config, **kwargs)
        try:
            yield
        finally:
            _program_state.config = old_config

    return override_config


@pytest_asyncio.fixture
async def postgres_connection(rhubarb) -> AsyncConnection:
    async with connection(timeout=1) as conn:
        async with conn.transaction(force_rollback=True):
            yield conn
