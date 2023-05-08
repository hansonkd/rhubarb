from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar

from psycopg import AsyncConnection

from rhubarb.config import config

conn_override: ContextVar[AsyncConnection | None] = ContextVar(
    "conn_override", default=None
)


@contextmanager
def override_conn(conn: AsyncConnection):
    prev = conn_override.get(None)
    conn_override.set(conn)
    yield
    conn_override.set(prev)


@asynccontextmanager
async def connection(timeout: float | None = None):
    if conn := conn_override.get(None):
        yield conn
        return
    pool = await config().postgres.get_pool()
    async with pool.connection(timeout=timeout) as conn:
        yield conn
