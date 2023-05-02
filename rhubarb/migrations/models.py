import datetime

import psycopg
from psycopg import Rollback, AsyncConnection

from rhubarb.crud import insert_objs
from rhubarb.model import BaseModel
from rhubarb.object_set import column, table, ObjectSet


@table
class AppliedMigration(BaseModel):
    __table__ = "rhubarb_migrations"
    migration_id: str = column()
    applied_on: datetime.datetime = column(insert_default="now()")


async def migration_was_applied(conn: AsyncConnection, migration_id: str) -> bool:
    async with conn.transaction() as inner_txn:
        try:
            os = await (
                ObjectSet(AppliedMigration, conn=conn)
                .where(lambda x: x.migration_id == migration_id)
                .one()
            )
        except psycopg.errors.UndefinedTable:
            os = None
            raise Rollback(inner_txn)
    return os is not None


async def mark_migration_as_applied(conn: AsyncConnection, migration_id: str) -> AppliedMigration:
    return await insert_objs(
        AppliedMigration, conn, [AppliedMigration(migration_id=migration_id)]
    ).execute(one=True)
