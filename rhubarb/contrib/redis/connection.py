from contextlib import asynccontextmanager

from rhubarb.config import config
from redis.asyncio import Redis


@asynccontextmanager
async def connection() -> Redis:
    pool = config().redis.get_pool()
    conn = Redis(connection_pool=pool)
    try:
        yield conn
    finally:
        await conn.close(close_connection_pool=False)
