import dataclasses

from redis.asyncio.client import Redis
from starlette_session import (
    SessionMiddleware as StarletteSessionMiddleware,
    BackendType,
)
from starlette.types import ASGIApp

from rhubarb.config import config


class SessionMiddleware(StarletteSessionMiddleware):
    def __init__(self, app: ASGIApp):
        conf = config()
        kwargs = dataclasses.asdict(conf.sessions)
        kwargs.pop("redis")
        kwargs["backend_type"] = BackendType.aioRedis
        kwargs["backend_client"] = Redis(connection_pool=conf.sessions.redis.get_pool())

        super().__init__(app=app, **kwargs)
