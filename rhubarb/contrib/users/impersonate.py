import enum

from psycopg import AsyncConnection
from starlette.requests import HTTPConnection

from rhubarb import RhubarbException
from rhubarb.contrib.audit.models import log_event, audit_connection
from rhubarb.contrib.users.models import U, get_user
from rhubarb.core import Unset
from rhubarb.errors import PermissionDenied


class ImpersonateEvent(enum.Enum):
    START_IMPERSONATING = "START_IMPERSONATING"
    STOP_IMPERSONATING = "STOP_IMPERSONATING"


IMPERSONATOR_SESSION_KEY = "impersonator_id"


async def impersonate(user: U, request: HTTPConnection) -> bool:
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise PermissionDenied(f"Current user {request.user} cannot impersonate")

    if user.is_superuser:
        raise PermissionDenied(f"Cannot impersonate superuser {request.user}")

    if not isinstance(user.id, Unset) and user.id:
        request.session["user_id"] = user.id
        request.session[IMPERSONATOR_SESSION_KEY] = request.user.id
        async with audit_connection() as audit_conn:
            await log_event(
                audit_conn,
                request=request,
                event_name=ImpersonateEvent.START_IMPERSONATING,
                variables={
                    "target": {
                        "id": user.identity,
                        "username": user.display_name,
                    }
                },
            )
        return True
    else:
        raise RhubarbException(
            f"Cannot impersonate {user} because it doesn't have an id"
        )


async def stop_impersonating(conn: AsyncConnection, request: HTTPConnection) -> bool:
    if impersonate_id := request.session.get(IMPERSONATOR_SESSION_KEY, None):
        user = await get_user(conn, impersonate_id)
        old_user = request.user
        request.session["user_id"] = user.id
        request.scope["user"] = user
        del request.session[IMPERSONATOR_SESSION_KEY]
        async with audit_connection() as audit_conn:
            await log_event(
                audit_conn,
                request=request,
                event_name=ImpersonateEvent.STOP_IMPERSONATING,
                variables={
                    "target": {
                        "id": old_user.identity,
                        "username": old_user.display_name,
                    }
                },
            )
        return True
    return False
