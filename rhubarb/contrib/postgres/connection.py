from contextlib import asynccontextmanager
from rhubarb.config import config


@asynccontextmanager
async def connection(timeout: float | None = None):
    pool = await config().postgres.get_pool()
    async with pool.connection(timeout=timeout) as conn:
        yield conn
