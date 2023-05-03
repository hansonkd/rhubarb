from contextlib import contextmanager
from typing import ContextManager, Callable

import pytest
import pytest_asyncio
from psycopg import AsyncConnection

from rhubarb.connection import connection
from rhubarb.config import _program_state, Config, PostgresConfig


@pytest.fixture(scope="session")
def rhubarb(config_override):
    with config_override(
        Config(
            postgres=PostgresConfig(
                host="localhost", dbname="debug", password="debug", user="debug"
            )
        )
    ):
        yield


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


@pytest_asyncio.fixture
async def postgres_connection(rhubarb) -> AsyncConnection:
    async with connection() as conn:
        async with conn.transaction(force_rollback=True):
            yield conn
