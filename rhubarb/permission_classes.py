import typing

from starlette.requests import Request
from starlette.websockets import WebSocket
from strawberry import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        request: typing.Union[Request, WebSocket] = info.context["request"]

        return hasattr(request, "user") and request.user.is_authenticated


class IsSuperUser(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        request: typing.Union[Request, WebSocket] = info.context["request"]

        return hasattr(request, "user") and request.user.is_authenticated and request.user.is_staff


class IsStaff(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        request: typing.Union[Request, WebSocket] = info.context["request"]

        return hasattr(request, "user") and request.user.is_authenticated and request.user.is_superuser
