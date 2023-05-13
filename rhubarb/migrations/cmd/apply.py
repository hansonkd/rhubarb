import argparse
import asyncio
import copy
import logging
import os
import sys

from rhubarb.config import config, init_rhubarb
from rhubarb.contrib.postgres.connection import connection
from rhubarb.migrations.data import MigrationStateDatabase
from rhubarb.migrations.utils import (
    load_migrations,
    current_migration_state,
    current_migration_queue,
)
from rhubarb.migrations.models import migration_was_applied, mark_migration_as_applied


async def run_migrations(create_extensions=True, check=False) -> bool:
    async with connection() as conn:
        if create_extensions and not check:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

        migration_dir = config().migration_directory
        meta_migration_dir = migration_dir / "meta"
        r = await do_apply_migrations(conn, meta_migration_dir, check)
        return await do_apply_migrations(conn, migration_dir, check) or r


async def do_apply_migrations(conn, migration_dir, check):
        head_migrations, current_migrations = load_migrations(migration_dir)
        current_state = current_migration_state(head_migrations, current_migrations)
        target_state = MigrationStateDatabase.from_registry(config().registry)
        q = list(current_migration_queue(
            head_migrations, current_migrations
        ))
        for migration_id in q:
            logging.info(f"Applying {migration_dir}, {migration_id}\n")
            migration = current_migrations[migration_id]

            was_applied = await migration_was_applied(conn, migration_id)
            if not was_applied:
                if migration.atomic:
                    async with conn.transaction(force_rollback=check):
                        for op in migration.operations:
                            await op.run(current_state, conn)
                            current_state = op.forward(copy.deepcopy(current_state))
                        await mark_migration_as_applied(conn, migration_id)
                else:
                    for op in migration.operations:
                        await op.run(current_state, conn)
                        current_state = op.forward(copy.deepcopy(current_state))
                    await mark_migration_as_applied(conn, migration_id)
        return target_state == current_state


if __name__ == "__main__":
    init_rhubarb(check=False)
    parser = argparse.ArgumentParser(
        prog="rhubarb.migrations.apply",
        description="Make new migrations based on the state of your program's tables",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Run the command but don't save the file. Return code reflects if a migration would have been made.",
    )
    parser.add_argument(
        "--skip-extensions",
        action="store_true",
        help="Skip creating the necessary extensions for UUID, etc.",
    )
    args = parser.parse_args()

    program_result = asyncio.run(
        run_migrations(check=args.check, create_extensions=not args.skip_extensions)
    )
    if program_result:
        sys.exit(os.CLD_EXITED)
    else:
        sys.exit(os.EX_OK)
