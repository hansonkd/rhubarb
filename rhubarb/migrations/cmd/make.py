import argparse
import logging
import os
import sys

from rhubarb.config import config, init_rhubarb
from rhubarb.migrations.data import MigrationStateDatabase
from rhubarb.migrations.utils import (
    generate_migration_file,
    current_migration_state,
    load_migrations,
)

try:
    from black import format_file_contents, FileMode

    use_black = True
except ImportError:
    use_black = False
    format_file_contents = None
    FileMode = None


def make_migration(check=False, empty=False) -> bool:
    migration_dir = config().migration_directory
    registry = config().registry
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
        logging.info(f"No migration to create.")
        return False

    fn, mig_file = result
    if check:
        logging.info(f"Skipping writing {fn} (check mode)")
    else:
        logging.info(f"Creating migration {fn}")
        if use_black:
            mig_file = format_file_contents(mig_file, fast=True, mode=FileMode())
        if not migration_dir.exists():
            migration_dir.mkdir(parents=True, exist_ok=True)
        with open(migration_dir / fn, "w") as f:
            f.write(mig_file)


if __name__ == "__main__":
    init_rhubarb()
    parser = argparse.ArgumentParser(
        prog="rhubarb.migrations.cmd.make",
        description="Make new migrations based on the state of your program's tables",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Run the command but don't save the file. Return code reflects if a migration would have been made.",
    )
    parser.add_argument(
        "-e",
        "--empty",
        action="store_true",
        help="Create an empty migration file if there are no changes",
    )
    args = parser.parse_args()

    logging.info(f"Running {parser.prog}")
    program_result = make_migration(empty=args.empty, check=args.check)
    if program_result:
        sys.exit(os.CLD_EXITED)
    else:
        sys.exit(os.EX_OK)
