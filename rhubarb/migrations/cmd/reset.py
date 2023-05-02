import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from rhubarb.connection import connection
from rhubarb.migrations.utils import current_migration_state, load_migrations, drop_tables_in_state


async def drop_tables(migration_dir="./migrations", check=False):
    async with connection() as conn:
        migration_dir = Path(migration_dir)
        head_migrations, current_migrations = load_migrations(migration_dir)
        current_state = current_migration_state(head_migrations, current_migrations)
        async with conn.transaction(force_rollback=check):
            await drop_tables_in_state(conn, current_state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='rhubarb.migrations.cmd.reset',
        description='Drop all tables in the current migration state.')
    parser.add_argument('-c', '--check', action='store_true', help="Run the command but don't save the file. Return code reflects if a migration would have been made.")
    args = parser.parse_args()

    program_result = asyncio.run(drop_tables(check=args.check))

    if program_result:
        sys.exit(os.CLD_EXITED)
    else:
        sys.exit(os.EX_OK)