import hashlib
import uuid
import datetime
from contextlib import asynccontextmanager
from typing import Optional

from strawberry.types.graphql import OperationType

from rhubarb import (
    BaseModel,
    column,
    table,
    Index,
    insert_objs,
    query,
    save,
    Registry,
    relation,
)
from rhubarb.config import config
from rhubarb.contrib.redis.cache import local_cache, local_only_cache
from rhubarb.core import SqlModel
from rhubarb.crud import by_pk
from rhubarb.local_cache import get_or_set_cache


@asynccontextmanager
async def audit_connection(timeout=30):
    pool = await config().audit.postgres.get_pool()
    async with pool.connection(timeout=timeout) as conn:
        yield conn


audit_registry = Registry(prefix="auditing_")


@table(registry=audit_registry)
class GqlQuery(SqlModel):
    __pk__ = "sha_hash"
    sha_hash: bytes = column()
    raw_query: str = column()


@table(registry=audit_registry)
class AuditEvent(BaseModel):
    timestamp: datetime.datetime = column(sql_default="now()")
    gql_query_sha_hash: bytes = column(sql_default=None)
    variables: Optional[dict] = column(sql_default=None)
    meta: Optional[dict] = column(sql_default=None)
    ip: Optional[str] = column(sql_default=None)
    session_id: Optional[str] = column(sql_default=None)
    user_id: Optional[uuid.UUID] = column(sql_default=None)
    impersonator_id: Optional[uuid.UUID] = column(sql_default=None)
    resource_url: Optional[str] = column(sql_default=None)
    operation_type: Optional[str] = column(sql_default=None)
    event_name: Optional[str] = column(sql_default=None)
    duration_ns: Optional[int] = column(sql_default=None)

    def __indexes__(self):
        return {
            "user_by_ts": Index(on=(self.user_id, self.timestamp)),
            "user_by_query": Index(on=(self.user_id, self.event_name, self.timestamp)),
            "by_query": Index(on=(self.event_name, self.timestamp)),
        }

    @relation
    def graphql_query(self, gql_query: GqlQuery):
        return self.gql_query_sha_hash == gql_query.sha_hash


@local_only_cache(key_arg="hash_digest")
async def do_get_or_create_gql_query(
    conn, raw_query: str, hash_digest: bytes = ...
) -> GqlQuery:
    gql_query = await by_pk(GqlQuery, hash_digest, conn).one()
    if not gql_query:
        gql_query = await save(
            GqlQuery(sha_hash=hash_digest, raw_query=raw_query),
            conn,
            insert_with_pk=True,
        ).execute()
    return gql_query


async def get_or_create_gql_query(conn, raw_query: str) -> GqlQuery:
    hash_digest = hashlib.sha1(raw_query.encode()).digest()
    return await do_get_or_create_gql_query(conn, raw_query, hash_digest=hash_digest)


async def log_gql_event(raw_query: str, operation_type: OperationType, **kwargs):
    if conn := kwargs.pop("conn", None):
        return await do_log_gql_event(conn, raw_query, operation_type, **kwargs)

    async with audit_connection(timeout=1) as conn:
        return await do_log_gql_event(conn, raw_query, operation_type, **kwargs)


async def do_log_gql_event(
    conn, raw_query: str, operation_type: OperationType, **kwargs
):
    conf = config()

    if operation_type == OperationType.MUTATION and not conf.audit.audit_mutations:
        return
    elif operation_type == OperationType.QUERY and not conf.audit.audit_queries:
        return
    elif (
        operation_type == OperationType.SUBSCRIPTION
        and not conf.audit.audit_subscriptions
    ):
        return
    gql_query = await get_or_create_gql_query(conn, raw_query)
    kwargs["gql_query_sha_hash"] = gql_query.sha_hash
    await log_event(conn, **kwargs)


async def log_event(conn, **kwargs):
    await insert_objs(AuditEvent, conn, [AuditEvent(**kwargs)], one=True).execute()
