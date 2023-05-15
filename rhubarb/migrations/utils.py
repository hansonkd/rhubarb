import copy
import datetime
import logging
import pprint
from collections import deque
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Iterator

from psycopg import AsyncConnection

from rhubarb.core import Unset
from rhubarb.migrations.data import (
    MigrationStateDatabase,
    Migration,
    AlterTable,
    MigrationOperation,
    DropColumn,
    CreateColumn,
    RenameTable,
    DropTable,
    CreateTable,
    SetMeta,
    SetDefault,
    AlterTypeUsing,
    DropDefault,
    AddReferencesConstraint,
    DropConstraint,
    AddConstraint,
    AddIndex,
    DropIndex,
)

from rhubarb.errors import RhubarbException
from rhubarb.object_set import Registry


def find_diffs(
    old_state: MigrationStateDatabase, new_state: MigrationStateDatabase
) -> list[MigrationOperation]:
    return list(iter_find_diffs(old_state, new_state))


def iter_find_diffs(
    old_state: MigrationStateDatabase, new_state: MigrationStateDatabase
) -> Iterator[MigrationOperation]:
    new_meta_kvs = {}
    new_meta_keys = new_state.meta.keys() - old_state.meta.keys()
    new_meta_kvs.update({k: new_state.meta[k] for k in new_meta_keys})
    new_meta_kvs.update(
        {k: v for k, v in old_state.meta.items() if new_state.meta[k] != v}
    )
    if new_meta_kvs:
        yield SetMeta(new_meta_kvs=new_meta_kvs)

    new_tables_keys = new_state.tables.keys() - old_state.tables.keys()
    for table_name, table_to_create in new_state.tables.items():
        if table_name not in new_tables_keys:
            continue
        yield CreateTable(
            schema=table_to_create.schema,
            name=table_to_create.name,
            class_name=table_to_create.class_name,
            primary_key=table_to_create.primary_key,
            constraints=table_to_create.constraints,
            indexes=table_to_create.indexes,
            columns=[
                CreateColumn(
                    name=c.name,
                    type=c.type,
                    python_name=c.python_name,
                    default=c.default,
                    references=c.references,
                )
                for c in table_to_create.columns.values()
            ],
        )

    deleted_tables_keys = old_state.tables.keys() - new_state.tables.keys()
    for table_name in deleted_tables_keys:
        table_to_delete = old_state.tables[table_name]
        yield DropTable(
            schema=table_to_delete.schema,
            name=table_to_delete.name,
        )

    altered_keys = old_state.tables.keys() & new_state.tables.keys()
    for table_name in altered_keys:
        old_table = old_state.tables[table_name]
        new_table = new_state.tables[table_name]
        altered_statements = []

        if new_table.class_name != old_table.class_name:
            yield RenameTable(
                schema=old_table.schema,
                old_name=old_table.name,
                new_name=new_table.name,
                new_class_name=new_table.class_name,
            )

        new_columns_names = new_table.columns.keys() - old_table.columns.keys()
        for column_name in new_columns_names:
            column_to_create = new_table.columns[column_name]
            altered_statements.append(
                CreateColumn(
                    name=column_to_create.name,
                    type=column_to_create.type,
                    python_name=column_to_create.python_name,
                    default=column_to_create.default,
                    references=column_to_create.references,
                )
            )

        deleted_column_names = old_table.columns.keys() - new_table.columns.keys()
        for column_name in deleted_column_names:
            columns_to_delete = old_table.columns[column_name]
            altered_statements.append(
                DropColumn(
                    name=columns_to_delete.name,
                )
            )

        kept_column_names = old_table.columns.keys() & new_table.columns.keys()
        for column_name in kept_column_names:
            old_column_value = old_table.columns[column_name]
            new_column_value = new_table.columns[column_name]
            if old_column_value.type != new_column_value.type:
                altered_statements.append(
                    AlterTypeUsing(name=column_name, new_type=new_column_value.type)
                )

            if old_column_value.references != new_column_value.references:
                if new_column_value.references:
                    if old_column_value.references:
                        altered_statements.append(
                            DropConstraint(
                                constraint_name=old_column_value.references.compute_constraint_name(
                                    column_name
                                )
                            )
                        )
                    altered_statements.append(
                        AddReferencesConstraint(
                            name=column_name,
                            references=new_column_value.references,
                            constraint_name=new_column_value.references.compute_constraint_name(
                                column_name
                            ),
                        )
                    )
                else:
                    altered_statements.append(
                        DropConstraint(
                            constraint_name=old_column_value.references.compute_constraint_name(
                                column_name
                            )
                        )
                    )

            if old_column_value.default != new_column_value.default:
                if not isinstance(new_column_value.default, Unset):
                    altered_statements.append(
                        SetDefault(
                            name=column_name,
                            default=new_column_value.default,
                            type=new_column_value.type,
                        )
                    )
                else:
                    altered_statements.append(DropDefault(name=column_name))

        new_constraints_names = (
            new_table.constraints.keys() - old_table.constraints.keys()
        )
        for constraint_name in new_constraints_names:
            constraint_to_create = new_table.constraints[constraint_name]
            altered_statements.append(
                AddConstraint(
                    constraint_name=constraint_name,
                    constraint=constraint_to_create,
                )
            )

        deleted_constraint_names = (
            old_table.constraints.keys() - new_table.constraints.keys()
        )
        for constraint_name in deleted_constraint_names:
            altered_statements.append(
                DropConstraint(
                    constraint_name=constraint_name,
                )
            )

        kept_constraint_names = (
            old_table.constraints.keys() & new_table.constraints.keys()
        )
        for constraint_name in kept_constraint_names:
            old_constraint = old_table.constraints[constraint_name]
            new_constraint = new_table.constraints[constraint_name]

            if old_constraint != new_constraint:
                altered_statements.append(
                    DropConstraint(
                        constraint_name=constraint_name,
                    )
                )
                altered_statements.append(
                    AddConstraint(
                        constraint_name=constraint_name, constraint=new_constraint
                    )
                )

        if altered_statements:
            yield AlterTable(
                schema=new_table.schema,
                name=new_table.name,
                alter_operations=altered_statements,
            )

        new_indexes_names = new_table.indexes.keys() - old_table.indexes.keys()
        for index_name in new_indexes_names:
            index_to_create = new_table.indexes[index_name]
            yield AddIndex(
                table_name=table_name,
                index_name=index_name,
                index=index_to_create,
            )

        deleted_indexes_names = old_table.indexes.keys() - new_table.indexes.keys()
        for index_name in deleted_indexes_names:
            yield DropIndex(
                table_name=table_name,
                index_name=index_name,
            )

        kept_index_names = old_table.indexes.keys() & new_table.indexes.keys()
        for index_name in kept_index_names:
            old_index = old_table.indexes[index_name]
            new_index = new_table.indexes[index_name]

            if old_index != new_index:
                yield DropIndex(
                    table_name=table_name,
                    index_name=index_name,
                )
                yield AddIndex(
                    table_name=table_name, index_name=index_name, index=new_index
                )


def run_operations(
    current_state: MigrationStateDatabase, ops: Iterator[MigrationOperation]
) -> MigrationStateDatabase:
    for op in ops:
        current_state = copy.deepcopy(current_state)
        current_state = op.forward(current_state)
    return current_state


MIGRATION_FILE_TEMPLATE = """# noqa\n# Generated by {program_name_version} on {timestamp:%Y/%m/%d-%H:%M:%S}

import rhubarb
from rhubarb import migrations
from rhubarb.migrations import *


def migrate():
    return migrations.Migration(
        depends_on={depends_on},
        operations=[
{operations_joined}
        ]
    )
"""


def generate_migration_file(
    old_state, new_state, migration_heads: list[str], empty: bool
):
    timestamp = datetime.datetime.utcnow()
    operations = find_diffs(old_state=old_state, new_state=new_state)
    if not operations and not empty:
        return

    operations_joined = ",\n            ".join(op.__as_py__() for op in operations)
    migration_id = f"migration_{timestamp:%Y%m%d-%H%M%S%f}"
    depends_on = str(migration_heads)
    return f"{migration_id}.py", MIGRATION_FILE_TEMPLATE.format(
        program_name_version="rhubarb 0.1.0",
        timestamp=timestamp,
        operations_joined=operations_joined,
        depends_on=depends_on,
    )


def load_migrations(migration_dir: Path):
    seen_deps = set()
    migrations = {}

    for migration_file in migration_dir.iterdir():
        if not migration_file.match("migration_*.py"):
            continue
        migration_id = migration_file.stem
        migration = SourceFileLoader(
            str(migration_dir.absolute()), str(migration_file)
        ).load_module()
        migration_obj: Migration = migration.migrate()
        seen_deps.update(migration_obj.depends_on)
        migrations[migration_id] = migration_obj

    head_of_migrations = migrations.keys() - seen_deps
    return head_of_migrations, migrations


def current_migration_queue(head_of_migrations, migrations) -> Iterator[str]:
    migration_queue = deque(head_of_migrations)
    apply_queue = deque(head_of_migrations)
    while migration_queue:
        work_on = migration_queue.popleft()
        migration = migrations[work_on]
        migration_queue.extend(migration.depends_on)
        apply_queue.extend(migration.depends_on)
    return reversed(apply_queue)


def current_migration_state(head_of_migrations, migrations) -> MigrationStateDatabase:
    state = MigrationStateDatabase(tables={})
    if len(head_of_migrations) > 1:
        raise RhubarbException(
            f"There are two heads of the migration tree. make a new migration to set {head_of_migrations} as dependencies"
        )

    if not head_of_migrations:
        return state

    apply_queue = current_migration_queue(head_of_migrations, migrations)
    for migration in apply_queue:
        for operation in migrations[migration].operations:
            state = operation.forward(copy.deepcopy(state))
    return state


def load_migration(migration_dir: Path, migration_id):
    migration_file = f"migration_{migration_id}.py"
    migration = SourceFileLoader(
        str(migration_dir.absolute()), str(migration_file)
    ).load_module()
    return migration.migrate()


async def reset_db_and_fast_forward(conn: AsyncConnection, registry: Registry):
    current_state = MigrationStateDatabase()
    new_state = MigrationStateDatabase.from_registry(registry)
    await drop_tables_in_state(conn, new_state)
    await fast_forward(conn, current_state, new_state)


async def fast_forward(
    conn: AsyncConnection,
    current_state: MigrationStateDatabase,
    new_state: MigrationStateDatabase,
) -> MigrationStateDatabase:
    for op in find_diffs(old_state=current_state, new_state=new_state):
        await op.run(current_state, conn)
        current_state = op.forward(current_state)
    return current_state


async def drop_tables_in_state(conn: AsyncConnection, state: MigrationStateDatabase):
    for _, table_name in state.tables.keys():
        logging.info(f"Dropping {table_name}")
        await conn.execute(f"DROP TABLE IF EXISTS {table_name}")


def run_checks(conf) -> bool:
    migration_dir = conf.migration_directory
    registry = conf.registry
    head_migrations, current_migrations = load_migrations(migration_dir)
    old_state = current_migration_state(head_migrations, current_migrations)
    new_state = MigrationStateDatabase.from_registry(registry)
    return bool(find_diffs(old_state, new_state))


def run_migration_checks(conf):
    migration_dir = conf.migration_directory
    head_migrations, current_migrations = load_migrations(migration_dir)
    old_state = current_migration_state(head_migrations, current_migrations)
    new_state = MigrationStateDatabase.from_registry(conf.registry)
    diffs = find_diffs(old_state, new_state)
    if bool(diffs):
        logging.warning("Found changes in datamodel that are not in migrations:\n" + pprint.pformat(diffs))
        logging.warning("run `python3 -m rhubarb.migrations.cmd.make` to generate them.")

    mig_queue = list(current_migration_queue(
        head_migrations, current_migrations
    ))
    for migration_id in mig_queue:
        logging.warning(f"Pending migration {migration_id}")
    if mig_queue:
        logging.warning("run `python3 -m rhubarb.migrations.cmd.make` to apply them.")
