from typing import Optional

from starlette.authentication import BaseUser, AuthCredentials
from starlette.middleware.authentication import (
    AuthenticationBackend,
    AuthenticationMiddleware,
)
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp

from rhubarb.pkg.postgres.connection import connection
from rhubarb.pkg.users.models import get_user


class SessionAuthenticationBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if user_id := conn.session.get("user_id"):
            async with connection() as conn:
                user = await get_user(conn, user_id)
            if not user:
                return None
            creds = ["authenticated", "user"]
            if user.is_staff:
                creds.append("staff")
            elif user.is_superuser:
                creds.append("superuser")
            return AuthCredentials(creds), user


class SessionAuthenticationMiddleware(AuthenticationMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app, backend=SessionAuthenticationBackend())
