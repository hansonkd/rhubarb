from contextlib import asynccontextmanager

from rhubarb.config import config


@asynccontextmanager
async def connection():
    conn = await config().redis.get_pool()
    yield conn
