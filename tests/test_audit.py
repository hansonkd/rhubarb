import dataclasses
import functools

import pytest
import pytest_asyncio
from strawberry.schema.config import StrawberryConfig

from rhubarb import query, Registry
from rhubarb.contrib.audit.config import AuditConfig
from rhubarb.contrib.audit.models import AuditEvent, GqlQuery, audit_registry
from rhubarb.contrib.audit.extensions import AuditingExtension
from rhubarb.contrib.postgres.connection import override_conn
from rhubarb.extension import TransactionalMutationExtension, TestingExtension
from rhubarb.migrations.utils import reset_db_and_fast_forward
from rhubarb.schema import ErrorRaisingSchema
from tests.conftest import Query, Mutation, testing_registry, DeleteException

test_registry = Registry()
test_registry.link(audit_registry)
test_registry.link(testing_registry)


@pytest.fixture
def audit_config(patch_config):
    audit_config = AuditConfig(reuse_conn=True)
    with patch_config(audit=audit_config):
        yield


@pytest_asyncio.fixture
async def audit_schema(postgres_connection, audit_config):
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, audit_registry)
        yield ErrorRaisingSchema(
            query=Query,
            mutation=Mutation,
            extensions=[
                functools.partial(TestingExtension, conn=postgres_connection),
                AuditingExtension,
            ],
            config=StrawberryConfig(auto_camel_case=False),
        )


@pytest_asyncio.fixture
async def audit_schema_transactional_rollback_event(postgres_connection, audit_config):
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, audit_registry)
        with override_conn(postgres_connection):
            yield ErrorRaisingSchema(
                query=Query,
                mutation=Mutation,
                extensions=[
                    functools.partial(TestingExtension, conn=postgres_connection),
                    AuditingExtension,
                    TransactionalMutationExtension,
                ],
                config=StrawberryConfig(auto_camel_case=False),
            )


@pytest_asyncio.fixture
async def audit_schema_transactional_dont_rollback_event(
    postgres_connection, audit_config
):
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, audit_registry)
        with override_conn(postgres_connection):
            yield ErrorRaisingSchema(
                query=Query,
                mutation=Mutation,
                extensions=[
                    functools.partial(TestingExtension, conn=postgres_connection),
                    TransactionalMutationExtension,
                    AuditingExtension,
                ],
                config=StrawberryConfig(auto_camel_case=False),
            )


@pytest.mark.asyncio
async def test_audit(audit_schema, postgres_connection, basic_data):
    conn = postgres_connection

    first_book = basic_data["books"][0]

    mutation = "mutation UpdateTitle($book_id: UUID!, $new_title: String!) { update_title(book_id: $book_id, new_title: $new_title) { title, author { name } } }"

    res = await audit_schema.execute(
        mutation,
        context_value={"conn": conn},
        variable_values={
            "book_id": str(first_book.id),
            "new_title": "Awesome title",
        },
    )

    assert res.errors is None

    @dataclasses.dataclass
    class Tmp:
        event: AuditEvent
        query: GqlQuery

    events: list[Tmp] = (
        await query(conn, AuditEvent)
        .select(lambda x: Tmp(event=x, query=x.graphql_query()))
        .as_list()
    )
    assert len(events) == 1
    assert events[0].event.variables["book_id"] == str(first_book.id)
    assert events[0].event.variables["new_title"] == "Awesome title"
    assert events[0].query.raw_query == mutation

    # Calling the same mutation again should result in the same GqlQuery object.
    res = await audit_schema.execute(
        mutation,
        context_value={"conn": conn},
        variable_values={
            "book_id": str(first_book.id),
            "new_title": "Awesome title",
        },
    )
    assert res.errors is None

    events: list[Tmp] = (
        await query(conn, AuditEvent)
        .select(lambda x: Tmp(event=x, query=x.graphql_query()))
        .as_list()
    )
    assert len(events) == 2

    assert events[0].query.raw_query == mutation
    assert events[1].query.raw_query == mutation

    assert events[0].event.gql_query_sha_hash == events[1].event.gql_query_sha_hash

    # Test a different mutation produces different hash
    other_mutation = "mutation UpdateTitle($book_id: UUID!, $new_title: String!) { update_title(book_id: $book_id, new_title: $new_title) { title} }"

    res = await audit_schema.execute(
        other_mutation,
        context_value={"conn": conn},
        variable_values={
            "book_id": str(first_book.id),
            "new_title": "Awesome title 2",
        },
    )
    assert res.errors is None

    events: list[Tmp] = (
        await query(conn, AuditEvent)
        .select(lambda x: Tmp(event=x, query=x.graphql_query()))
        .as_list()
    )
    assert len(events) == 3

    assert events[-1].query.raw_query == other_mutation
    assert events[-1].event.variables["book_id"] == str(first_book.id)
    assert events[-1].event.variables["new_title"] == "Awesome title 2"
    assert events[0].event.gql_query_sha_hash != events[-1].event.gql_query_sha_hash


@pytest.mark.asyncio
async def test_audit_rollback(
    audit_schema_transactional_rollback_event, postgres_connection, basic_data
):
    conn = postgres_connection
    audit_schema = audit_schema_transactional_rollback_event

    first_book = basic_data["books"][0]

    with pytest.raises(DeleteException):
        await audit_schema.execute(
            "mutation Delete($book_id: UUID!) { delete_book_raises(book_id: $book_id) }",
            context_value={"conn": conn},
            variable_values={
                "book_id": str(first_book.id),
            },
        )

    events = await query(conn, AuditEvent).as_list()
    assert len(events) == 0


@pytest.mark.asyncio
async def test_audit_dont_rollback(
    audit_schema_transactional_dont_rollback_event, postgres_connection, basic_data
):
    conn = postgres_connection
    audit_schema = audit_schema_transactional_dont_rollback_event

    first_book = basic_data["books"][0]

    with pytest.raises(DeleteException):
        await audit_schema.execute(
            "mutation Delete($book_id: UUID!) { delete_book_raises(book_id: $book_id) }",
            context_value={"conn": conn},
            variable_values={
                "book_id": str(first_book.id),
            },
        )

    events = await query(conn, AuditEvent).as_list()
    assert len(events) == 1
