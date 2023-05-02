import argparse
import os
import sys
from pathlib import Path

from rhubarb.migrations.data import MigrationStateDatabase
from rhubarb.migrations.utils import generate_migration_file, current_migration_state, load_migrations
from rhubarb.object_set import Registry


def make_migration(migration_dir="./migrations", check=False, empty=False, registry: Registry = None) -> bool:
    migration_dir = Path(migration_dir)
    head_migrations, current_migrations = load_migrations(migration_dir)
    old_state = current_migration_state(head_migrations, current_migrations)
    new_state = MigrationStateDatabase.from_registry(registry)

    result = generate_migration_file(
        old_state=old_state,
        new_state=new_state,
        migration_heads=list(head_migrations),
        empty=empty,
    )
    if result is None:
        return False

    fn, mig_file = result
    if not check:
        with open(migration_dir / fn, "w") as f:
            f.write(mig_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='rhubarb.migrations.make',
        description='Make new migrations based on the state of your program\'s tables')
    parser.add_argument('-c', '--check', action='store_true', help="Run the command but don't save the file. Return code reflects if a migration would have been made.")
    parser.add_argument('-e', '--empty', action='store_true', help="Create an empty migration file if there are no changes")
    args = parser.parse_args()

    program_result = make_migration(empty=args.empty, check=args.check)
    if program_result:
        sys.exit(os.CLD_EXITED)
    else:
        sys.exit(os.EX_OK)
