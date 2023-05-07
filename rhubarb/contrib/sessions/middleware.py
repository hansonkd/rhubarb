import dataclasses

from starlette_session import SessionMiddleware as StarletteSessionMiddleware
from starlette.types import ASGIApp

from rhubarb.config import config


class SessionMiddleware(StarletteSessionMiddleware):
    def __init__(self, app: ASGIApp):
        kwargs = dataclasses.asdict(config().sessions)

        super().__init__(app=app, **kwargs)
