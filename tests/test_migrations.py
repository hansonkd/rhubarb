from typing import Optional

import pytest

from rhubarb.migrations.data import (
    MigrationStateDatabase,
    CreateTable,
    AlterTable,
    CreateColumn,
    DropColumn,
    AddIndex,
    AddConstraint,
    DropIndex,
    DropConstraint,
    AlterTypeUsing,
    SetDefault,
    DropDefault,
    DropTable,
    AddReferencesConstraint,
)
from rhubarb.migrations.utils import find_diffs, reset_db_and_fast_forward, fast_forward
from rhubarb.model import BaseUpdatedAtModel
from rhubarb.object_set import (
    table,
    Registry,
    column,
    References,
    Index,
    Constraint,
    ModelSelector,
)

migrations_registry = Registry()


@table(registry=migrations_registry)
class RatingModel(BaseUpdatedAtModel):
    rating: int = column()


EMPTY_STATE = MigrationStateDatabase()
REFERENCE_STATE = MigrationStateDatabase.from_registry(migrations_registry)


@pytest.mark.asyncio
async def test_create_table(postgres_connection):
    diffs = find_diffs(old_state=EMPTY_STATE, new_state=REFERENCE_STATE)
    assert len(diffs) == 1
    assert isinstance(diffs[0], CreateTable)
    async with postgres_connection.transaction(force_rollback=True):
        await fast_forward(postgres_connection, EMPTY_STATE, REFERENCE_STATE)



@pytest.mark.asyncio
async def test_drop_table(postgres_connection):
    diffs = find_diffs(old_state=REFERENCE_STATE, new_state=EMPTY_STATE)
    assert len(diffs) == 1
    assert isinstance(diffs[0], DropTable)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        await fast_forward(postgres_connection, REFERENCE_STATE, EMPTY_STATE)


@pytest.mark.asyncio
async def test_change_type(postgres_connection):
    changed_registry = Registry()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: bool = column()

    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=REFERENCE_STATE, new_state=new_state)
    assert len(diffs) == 1
    assert isinstance(diffs[0], AlterTable)
    assert len(diffs[0].alter_operations) == 1
    assert isinstance(diffs[0].alter_operations[0], AlterTypeUsing)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        await fast_forward(postgres_connection, REFERENCE_STATE, new_state)


@pytest.mark.asyncio
async def test_change_default(postgres_connection):
    first_registry = Registry()

    @table(registry=first_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: Optional[int] = column()

    changed_registry = Registry()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: Optional[int] = column(sql_default=None)

    old_state = MigrationStateDatabase.from_registry(first_registry)
    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=old_state, new_state=new_state)
    assert len(diffs) == 1
    assert isinstance(diffs[0], AlterTable)
    assert len(diffs[0].alter_operations) == 1
    assert isinstance(diffs[0].alter_operations[0], SetDefault)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, first_registry)
        await fast_forward(postgres_connection, old_state, new_state)

    diffs = find_diffs(old_state=new_state, new_state=old_state)
    assert len(diffs) == 1
    assert isinstance(diffs[0], AlterTable)
    assert len(diffs[0].alter_operations) == 1
    assert isinstance(diffs[0].alter_operations[0], DropDefault)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, changed_registry)
        await fast_forward(postgres_connection, new_state, old_state)


@pytest.mark.asyncio
async def test_add(postgres_connection):
    changed_registry = Registry()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: int = column()
        rating2: int = column()

    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=REFERENCE_STATE, new_state=new_state)
    assert len(diffs) == 1
    assert isinstance(diffs[0], AlterTable)
    assert len(diffs[0].alter_operations) == 1
    assert isinstance(diffs[0].alter_operations[0], CreateColumn)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        await fast_forward(postgres_connection, REFERENCE_STATE, new_state)


@pytest.mark.asyncio
async def test_drop_and_add(postgres_connection):
    changed_registry = Registry()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating2: int = column()

    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=REFERENCE_STATE, new_state=new_state)
    assert len(diffs) == 1
    assert isinstance(diffs[0], AlterTable)
    assert len(diffs[0].alter_operations) == 2
    assert isinstance(diffs[0].alter_operations[1], DropColumn)
    assert isinstance(diffs[0].alter_operations[0], CreateColumn)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        await fast_forward(postgres_connection, REFERENCE_STATE, new_state)


@pytest.mark.asyncio
async def test_add_constraint(postgres_connection):
    changed_registry = Registry()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: int = column()

        def __constraints__(self: ModelSelector):
            return {"only_positive_ratings": Constraint(check=self.rating > 0)}

    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=REFERENCE_STATE, new_state=new_state)
    assert len(diffs) == 1
    assert isinstance(diffs[0], AlterTable)
    assert len(diffs[0].alter_operations) == 1
    assert isinstance(diffs[0].alter_operations[0], AddConstraint)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        await fast_forward(postgres_connection, REFERENCE_STATE, new_state)


@pytest.mark.asyncio
async def test_add_index(postgres_connection):
    changed_registry = Registry()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: int = column()

        def __indexes__(self):
            return {"awesome_index": Index(on=self.rating - 1, concurrently=False)}

    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=REFERENCE_STATE, new_state=new_state)
    assert len(diffs) == 1
    assert isinstance(diffs[0], AddIndex)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        await fast_forward(postgres_connection, REFERENCE_STATE, new_state)



@pytest.mark.asyncio
async def test_delete_index(postgres_connection):
    changed_registry = Registry()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: int = column()

        def __indexes__(self):
            return {"awesome_index": Index(on=self.rating - 1)}

    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=new_state, new_state=REFERENCE_STATE)
    assert len(diffs) == 1
    assert isinstance(diffs[0], DropIndex)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, changed_registry)
        await fast_forward(postgres_connection, new_state, REFERENCE_STATE)


@pytest.mark.asyncio
async def test_drop_constraint(postgres_connection):
    changed_registry = Registry()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: int = column()

        def __constraints__(self: ModelSelector):
            return {"only_positive_ratings": Constraint(check=self.rating > 0)}

    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=new_state, new_state=REFERENCE_STATE)
    assert len(diffs) == 1
    assert isinstance(diffs[0], AlterTable)
    assert len(diffs[0].alter_operations) == 1
    assert isinstance(diffs[0].alter_operations[0], DropConstraint)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, changed_registry)
        await fast_forward(postgres_connection, new_state, REFERENCE_STATE)


@pytest.mark.asyncio
async def test_add_fk(postgres_connection):
    changed_registry = Registry()

    @table(registry=changed_registry)
    class OtherModel(BaseUpdatedAtModel):
        id: int = column()

    @table(registry=changed_registry)
    class RatingModel(BaseUpdatedAtModel):
        rating: int = column(references=References(OtherModel.__table__))

    new_state = MigrationStateDatabase.from_registry(changed_registry)
    diffs = find_diffs(old_state=REFERENCE_STATE, new_state=new_state)
    assert len(diffs) == 2
    assert isinstance(diffs[0], CreateTable)
    assert isinstance(diffs[1], AlterTable)
    assert len(diffs[1].alter_operations) == 1
    assert isinstance(diffs[1].alter_operations[0], AddReferencesConstraint)
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        await fast_forward(postgres_connection, REFERENCE_STATE, new_state)
