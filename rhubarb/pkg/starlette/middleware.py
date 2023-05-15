import dataclasses

from rhubarb.config import config
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware


class CORSMiddleware(StarletteCORSMiddleware):
    def __init__(self, app):
        conf = config().cors
        kwargs = dataclasses.asdict(conf)
        super().__init__(app, **kwargs)
