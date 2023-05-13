import functools
import uuid

import pytest
import pytest_asyncio
from starlette.middleware import Middleware
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info

import rhubarb
from httpx import AsyncClient
from starlette.applications import Starlette
from starlette.routing import Route

from rhubarb import Registry, table, get_conn, save, query
from rhubarb.contrib.audit.config import AuditConfig
from rhubarb.contrib.audit.extensions import AuditingExtension
from rhubarb.contrib.audit.models import audit_registry, AuditEvent
from rhubarb.contrib.postgres.connection import override_conn
from rhubarb.contrib.sessions.middleware import SessionMiddleware
from rhubarb.contrib.starlette.asgi import GraphQL

from rhubarb.contrib.users.backends import login
from rhubarb.contrib.users.config import UserConfig
from rhubarb.contrib.users.impersonate import (
    impersonate,
    stop_impersonating,
    ImpersonateEvent,
)
from rhubarb.contrib.users.middleware import (
    SessionAuthenticationMiddleware,
)
from rhubarb.contrib.users.models import user_registry, User, get_user
from rhubarb.extension import RhubarbTestingExtension
from rhubarb.migrations.utils import reset_db_and_fast_forward
from rhubarb.schema import ErrorRaisingSchema

migrations_registry = Registry()
migrations_registry.link(user_registry)
migrations_registry.link(audit_registry)


@table(registry=migrations_registry)
class MyUser(User):
    pass


@rhubarb.type
class Query:
    @rhubarb.field
    def current_user(self, info: Info) -> MyUser | None:
        if info.context["request"].user.is_authenticated:
            return info.context["request"].user
        return None


@rhubarb.type
class Mutation:
    @rhubarb.mutation
    async def login(self, user_id: uuid.UUID, info: Info) -> MyUser:
        conn = get_conn(info)
        user = await get_user(conn, user_id)
        return await login(conn, user, info.context["request"])

    @rhubarb.mutation
    async def impersonate(self, user_id: uuid.UUID, info: Info) -> MyUser:
        conn = get_conn(info)
        user = await get_user(conn, user_id)
        if await impersonate(user, info.context["request"]):
            return user

    @rhubarb.mutation
    async def stop_impersonating(self, info: Info) -> bool:
        conn = get_conn(info)
        return await stop_impersonating(conn, info.context["request"])

    @rhubarb.mutation
    async def other_mutation(self) -> bool:
        return True


@pytest.fixture
def user_config(patch_config):
    audit_config = AuditConfig(reuse_conn=True)
    with patch_config(users=UserConfig(user_model=MyUser), audit=audit_config):
        yield


@pytest_asyncio.fixture
async def user_table(postgres_connection, user_config):
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        yield


@pytest_asyncio.fixture
async def user(postgres_connection, user_table) -> MyUser:
    yield await save(postgres_connection, MyUser(username="la@example.com")).execute()


@pytest_asyncio.fixture
async def superuser(postgres_connection, user_table) -> MyUser:
    yield await save(
        postgres_connection,
        MyUser(username="admin@example.com", is_staff=True, is_superuser=True),
    ).execute()


class OverrideMiddleware:
    def __init__(self, app, conn=None):
        self.app = app
        self.conn = conn

    async def __call__(self, scope, receive, send):
        with override_conn(self.conn):
            await self.app(scope, receive, send)


@pytest_asyncio.fixture
async def async_http_client(postgres_connection) -> AsyncClient:
    schema = ErrorRaisingSchema(
        query=Query,
        mutation=Mutation,
        extensions=[
            functools.partial(RhubarbTestingExtension, conn=postgres_connection),
            AuditingExtension,
        ],
        config=StrawberryConfig(auto_camel_case=False),
    )

    app = Starlette(
        middleware=[
            Middleware(OverrideMiddleware, conn=postgres_connection),
            Middleware(SessionMiddleware),
            Middleware(SessionAuthenticationMiddleware),
        ],
        routes=[Route("/graphql/", GraphQL(schema, debug=True))],
    )

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_current_user_none(async_http_client: AsyncClient, user_table):
    res = await async_http_client.post(
        "/graphql/", json={"query": "query { current_user { first_name } }"}
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert not data["data"]["current_user"]


@pytest.mark.asyncio
async def test_current_user_logged_in(async_http_client: AsyncClient, user):
    res = await async_http_client.post(
        "/graphql/",
        json={
            "query": "mutation Login($user_id: UUID!) { login(user_id: $user_id) { id } }",
            "variables": {"user_id": str(user.id)},
        },
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["login"]
    assert data["data"]["login"]["id"] == str(user.id)

    res = await async_http_client.post(
        "/graphql/", json={"query": "query { current_user { id } }"}
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["current_user"]


@pytest.mark.asyncio
async def test_current_user_impersonate(
    postgres_connection, async_http_client: AsyncClient, user_config, user, superuser
):
    res = await async_http_client.post(
        "/graphql/",
        json={
            "query": "mutation Login($user_id: UUID!) { login(user_id: $user_id) { id } }",
            "variables": {"user_id": str(superuser.id)},
        },
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["login"]
    assert data["data"]["login"]["id"] == str(superuser.id)

    res = await async_http_client.post(
        "/graphql/", json={"query": "query { current_user { id } }"}
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["current_user"]
    assert data["data"]["current_user"]["id"] == str(superuser.id)

    res = await async_http_client.post(
        "/graphql/",
        json={
            "query": "mutation Impersonate($user_id: UUID!) { impersonate(user_id: $user_id) { id } }",
            "variables": {"user_id": str(user.id)},
        },
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["impersonate"]
    assert data["data"]["impersonate"]["id"] == str(user.id)

    res = await async_http_client.post(
        "/graphql/", json={"query": "query { current_user { id } }"}
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["current_user"]
    assert data["data"]["current_user"]["id"] == str(user.id)

    events: list[AuditEvent] = await query(postgres_connection, AuditEvent).as_list()
    assert len(events) == 4
    assert events[-2].event_name == ImpersonateEvent.START_IMPERSONATING.value
    assert events[-2].user_id == superuser.id

    # Test impersonate
    res = await async_http_client.post(
        "/graphql/",
        json={
            "query": "mutation OtherMutation { other_mutation }",
            "variables": {},
        },
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["other_mutation"]

    events: list[AuditEvent] = await query(postgres_connection, AuditEvent).as_list()
    assert len(events) == 5
    assert events[-1].event_name == "OtherMutation"
    assert events[-1].user_id == user.id
    assert events[-1].impersonator_id == superuser.id

    # Stop impersonate
    res = await async_http_client.post(
        "/graphql/",
        json={
            "query": "mutation StopImpersonate { stop_impersonating }",
            "variables": {},
        },
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["stop_impersonating"]

    events: list[AuditEvent] = await query(postgres_connection, AuditEvent).as_list()
    assert len(events) == 7
    assert events[-2].event_name == ImpersonateEvent.STOP_IMPERSONATING.value

    res = await async_http_client.post(
        "/graphql/", json={"query": "query { current_user { id } }"}
    )
    data = res.json()
    assert not "errors" in data
    assert "data" in data
    assert data["data"]["current_user"]
    assert data["data"]["current_user"]["id"] == str(superuser.id)
