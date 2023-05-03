import argparse
import asyncio
import copy
import logging
import os
import sys

from rhubarb.config import config
from rhubarb.connection import connection
from rhubarb.migrations.data import MigrationStateDatabase
from rhubarb.migrations.utils import (
    load_migrations,
    current_migration_state,
    current_migration_queue,
)
from rhubarb.migrations.models import migration_was_applied, mark_migration_as_applied


async def run_migrations(check=False) -> bool:
    async with connection() as conn:
        migration_dir = config().migration_directory
        head_migrations, current_migrations = load_migrations(migration_dir)
        current_state = current_migration_state(head_migrations, current_migrations)
        target_state = MigrationStateDatabase.from_registry(config().registry)

        for migration_id in current_migration_queue(
            head_migrations, current_migrations
        ):
            logging.info(f"Applying {migration_id}")
            migration = current_migrations[migration_id]

            was_applied = migration_was_applied(conn, migration_id)
            if not was_applied:
                if migration.atomic:
                    async with conn.transaction(force_rollback=check):
                        for op in migration.operations:
                            await op.run(current_state, conn)
                            current_state = op.forward(copy.deepcopy(current_state))
                else:
                    for op in migration.operations:
                        await op.run(current_state, conn)
                        current_state = op.forward(copy.deepcopy(current_state))
                await mark_migration_as_applied(conn, migration_id)
        return target_state == current_state


if __name__ == "__main__":
    init_rhubarb()
    parser = argparse.ArgumentParser(
        prog="rhubarb.migrations.make",
        description="Make new migrations based on the state of your program's tables",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Run the command but don't save the file. Return code reflects if a migration would have been made.",
    )
    args = parser.parse_args()

    program_result = asyncio.run(run_migrations(check=args.check))
    if program_result:
        sys.exit(os.CLD_EXITED)
    else:
        sys.exit(os.EX_OK)
