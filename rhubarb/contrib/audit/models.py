import hashlib
import uuid
import datetime
from contextlib import asynccontextmanager
from typing import Optional

from strawberry.types.graphql import OperationType

from rhubarb import BaseModel, column, table, Index, insert_objs, query, save
from rhubarb.config import config
from rhubarb.core import SqlModel
from rhubarb.crud import by_pk
from rhubarb.local_cache import get_or_set_cache


@asynccontextmanager
async def audit_connection():
    pool = await config().audit.postgres.get_pool()
    async with pool.connection() as conn:
        yield conn


@table
class GqlQuery(SqlModel):
    __pk__ = "sha_hash"
    sha_hash: bytes = column()
    raw_query: str = column()


@table
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

    def __indexes__(self):
        return {
            "user_by_ts": Index(on=(self.user_id, self.timestamp)),
            "user_by_query": Index(on=(self.user_id, self.event_name, self.timestamp)),
            "by_query": Index(on=(self.event_name, self.timestamp)),
        }


async def get_or_create_gql_query(conn, raw_query: str) -> GqlQuery:
    hash_digest = hashlib.sha1(raw_query.encode()).digest()

    async def load_from_db():
        gql_query = await by_pk(GqlQuery, hash_digest, conn).one()
        if not gql_query:
            gql_query = await save(
                GqlQuery(sha_hash=hash_digest, raw_query=query), conn
            ).execute()
        return gql_query

    return await get_or_set_cache(("gql_queries", hash_digest), load_from_db)


async def log_gql_event(raw_query: str, operation_type: OperationType, **kwargs):
    conf = config()
    async with audit_connection() as conn:
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
    await insert_objs(AuditEvent, conn, [AuditEvent(**kwargs)], one=True)
