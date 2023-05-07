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

from rhubarb import Registry, table, get_conn, save
from rhubarb.contrib.postgres.connection import override_conn
from rhubarb.contrib.sessions.middleware import SessionMiddleware
from strawberry.asgi import GraphQL

from rhubarb.contrib.users.backends import login
from rhubarb.contrib.users.config import UserConfig
from rhubarb.contrib.users.middleware import (
    SessionAuthenticationMiddleware,
    SessionAuthenticationBackend,
)
from rhubarb.contrib.users.models import user_registry, User, get_user
from rhubarb.migrations.utils import reset_db_and_fast_forward
from rhubarb.schema import ErrorRaisingSchema

migrations_registry = Registry()
migrations_registry.link(user_registry)


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


@pytest.fixture
def user_config(patch_config):
    with patch_config(users=UserConfig(user_model=MyUser)):
        yield


@pytest_asyncio.fixture
async def user_table(postgres_connection, user_config):
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        yield


@pytest_asyncio.fixture
async def user(postgres_connection, user_table) -> MyUser:
    yield await save(MyUser(username="la@example.com"), postgres_connection).execute()


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
