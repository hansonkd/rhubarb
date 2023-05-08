import datetime

from psycopg import AsyncConnection
from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    AuthCredentials,
)
from starlette.requests import HTTPConnection

from rhubarb import save, RhubarbException
from rhubarb.contrib.postgres.connection import connection
from rhubarb.contrib.users.models import get_user, U
from rhubarb.core import Unset


class SessionAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if user_id := conn.session.get("user_id"):
            async with connection() as conn:
                if user := await get_user(conn, user_id):
                    return AuthCredentials(["authenticated"]), user
                raise AuthenticationError(f"User not found")


async def login(conn: AsyncConnection, user: U, request: HTTPConnection) -> U:
    if not isinstance(user.id, Unset) and user.id:
        request.session["user_id"] = user.id
    else:
        raise RhubarbException(f"Cannot login {user} because it doesn't have an id")
    user.last_login = datetime.datetime.utcnow()
    return await save(user, conn).execute()
