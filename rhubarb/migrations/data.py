import copy
import inspect
import pprint
from typing import Callable, Type, Any, Awaitable, Optional, Self
from rhubarb.core import SqlModel, T, UNSET, DEFAULT_SQL_FUNCTION, Unset
from rhubarb.errors import RhubarbException
from rhubarb.object_set import (
    SQLBuilder,
    SqlType,
    DEFAULT_REGISTRY,
    ColumnField,
    column,
    columns,
    pk_column_names,
    Index,
    Constraint,
    ObjectSet,
    References,
    ON_DELETE,
)
from rhubarb.object_set import table as table_decorator
import dataclasses
from psycopg import AsyncConnection


@dataclasses.dataclass(frozen=True)
class FrozenReference:
    table_name: str | None
    constraint_name: str | None = None
    on_delete: ON_DELETE | None = None

    @classmethod
    def from_reference(cls, reference: References) -> Optional[Self]:
        if reference:
            return cls(
                table_name=reference.real_table_name,
                constraint_name=reference.constraint_name,
                on_delete=reference.on_delete,
            )

    def as_reference(self) -> References:
        return References(
            self.table_name,
            constraint_name=self.constraint_name,
            on_delete=self.on_delete,
        )

    def compute_constraint_name(self, column_name: str):
        if self.constraint_name:
            return self.constraint_name
        return f"{column_name}_fk"


@dataclasses.dataclass
class MigrationStateColumn:
    name: str
    python_name: str
    type: SqlType
    default: DEFAULT_SQL_FUNCTION | None = None
    references: FrozenReference | None = None

    def as_column_field(self) -> ColumnField:
        return column(
            virtual=False,
            column_name=self.name,
            python_name=self.python_name,
            references=self.references and self.references.as_reference(),
        )


@dataclasses.dataclass(frozen=True)
class MigrationStateTable:
    schema: str
    name: str
    class_name: str
    primary_key: tuple[str, ...]
    columns: dict[str, MigrationStateColumn]
    constraints: dict[str, "MigrationConstraint"] = dataclasses.field(
        default_factory=dict
    )
    indexes: dict[str, "MigrationIndex"] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class MigrationStateDatabase:
    tables: dict[(str, str), MigrationStateTable] = dataclasses.field(
        default_factory=dict
    )
    meta: dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_registry(cls, registry=None):
        registry = registry or DEFAULT_REGISTRY
        tables = {}
        for model in registry.values(set()):
            if getattr(model, "__managed__", True):
                state_m = state_from_table(model)
                tables[(state_m.schema, state_m.name)] = state_m
        return cls(tables=tables)


ALL_OPERATIONS = {}


def register_operation(t):
    ALL_OPERATIONS[t.__name__] = t
    return t


def state_from_table(m: Type[T]):
    cols = {}
    for column_field in columns(m, virtual=False):
        default = (
            UNSET
            if column_field.sql_default == dataclasses.MISSING
            else column_field.sql_default
        )
        cols[column_field.column_name] = MigrationStateColumn(
            name=column_field.column_name,
            type=column_field.column_type,
            default=default,
            python_name=column_field.python_name,
            references=FrozenReference.from_reference(column_field.references),
        )

    pk = tuple(pk_column_names(m))
    schema = m.__schema__
    name = m.__table__
    pks = ", ".join(pk)
    constraints = {
        f"{name}_pk": MigrationConstraint(check=f"{pks}", primary_key=True)
    }
    if hasattr(m, "__constraints__"):
        os = ObjectSet(m, None)
        additional_constraints = m.__constraints__(os.model_selector)
        for k, v in additional_constraints.items():
            if not isinstance(v, Constraint):
                raise RhubarbException(
                    f"__constraints__ should return a dict[str, Constraint]. Got {v}"
                )
            constraints.setdefault(k, MigrationConstraint.from_constraint(v))

    indexes = {}
    if hasattr(m, "__indexes__"):
        os = ObjectSet(m, None)
        additional_indexes = m.__indexes__(os.model_selector)
        for k, v in additional_indexes.items():
            if not isinstance(v, Index):
                raise RhubarbException(
                    f"__indexes__ should return a dict[str, Index]. Got {v}"
                )
            indexes.setdefault(k, MigrationIndex.from_index(v))

    return MigrationStateTable(
        schema=schema,
        name=name,
        primary_key=pk,
        columns=cols,
        class_name=m.__name__,
        indexes=indexes,
        constraints=constraints,
    )


@register_operation
@dataclasses.dataclass(frozen=True)
class MigrationOperation:
    def __as_py__(self) -> str:
        param_str = "\n               ".join(pprint.pformat(self).split("\n"))
        return f"            {param_str}"

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        raise NotImplementedError

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class AlterOperation:
    def __sql__(self, table: MigrationStateTable) -> MigrationStateDatabase:
        pass

    def alter(self, table: MigrationStateTable) -> MigrationStateDatabase:
        pass


@dataclasses.dataclass(frozen=True)
class CreateColumn(AlterOperation):
    name: str
    python_name: str
    type: SqlType
    default: DEFAULT_SQL_FUNCTION | None = None
    references: FrozenReference = None

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"ADD COLUMN {self.name} {self.type.sql}")
        if self.type.optional:
            builder.write(" NULL")
        else:
            builder.write(" NOT NULL")

        if not isinstance(self.default, Unset):
            default = self.default
            if isinstance(default, str):
                builder.write(f" DEFAULT {default}")
            else:
                builder.write(f" DEFAULT ")
                builder.write_value(default, self.type)

        if self.references:
            builder.write(f" REFERENCES {self.references.table_name}")

            if self.references.on_delete:
                builder.write(f" ON DELETE {self.references.on_delete}")

    def alter(self, table: MigrationStateTable) -> MigrationStateTable:
        columns = copy.copy(table.columns)
        columns[self.name] = MigrationStateColumn(
            name=self.name,
            type=self.type,
            default=self.default,
            python_name=self.python_name,
            references=self.references,
        )
        return dataclasses.replace(table, columns=columns)


@dataclasses.dataclass(frozen=True)
class DropColumn:
    name: str

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"DROP COLUMN {self.name}")

    def alter(self, table):
        columns = copy.copy(table.columns)
        columns.pop(self.name)
        return dataclasses.replace(table, columns=columns)


@dataclasses.dataclass(frozen=True)
class AlterTypeUsing:
    name: str
    new_type: SqlType
    using: str | None = None

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"ALTER {self.name} TYPE ")
        self.new_type.__sql__(builder)
        if self.using is None:
            using = f"{self.name}::TEXT::{self.new_type.sql}"
        else:
            using = self.using
        builder.write(f" USING {using}")

    def alter(self, table):
        columns = copy.copy(table.columns)
        col = columns.pop(self.name)
        new_col = dataclasses.replace(col, type=self.new_type)
        columns[self.name] = new_col
        return dataclasses.replace(table, columns=columns)


@dataclasses.dataclass(frozen=True)
class SetDefault:
    name: str
    type: SqlType
    default: DEFAULT_SQL_FUNCTION | None = None

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"ALTER {self.name} SET ")
        default = self.default
        if isinstance(default, str):
            builder.write(f" DEFAULT {default}")
        else:
            builder.write(f" DEFAULT ")
            builder.write_value(default, self.type)

    def alter(self, table):
        columns = copy.copy(table.columns)
        col = columns.pop(self.name)
        new_col = dataclasses.replace(col, default=self.default)
        columns[self.name] = new_col
        return dataclasses.replace(table, columns=columns)


@dataclasses.dataclass(frozen=True)
class DropDefault:
    name: str

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"ALTER {self.name} DROP DEFAULT")

    def alter(self, table):
        columns = copy.copy(table.columns)
        col = columns.pop(self.name)
        new_col = dataclasses.replace(col, default=UNSET)
        columns[self.name] = new_col
        return dataclasses.replace(table, columns=columns)


@dataclasses.dataclass(frozen=True)
class AddConstraint:
    constraint_name: str
    constraint: "MigrationConstraint"

    def __sql__(self, builder: SQLBuilder):
        builder.write(
            f"ADD CONSTRAINT {self.constraint_name} {self.constraint.modifier} ({self.constraint.check})"
        )

    def alter(self, table: MigrationStateTable):
        new_constraints = copy.copy(table.constraints)
        new_constraints[self.constraint_name] = self.constraint
        return dataclasses.replace(table, constraints=new_constraints)


@dataclasses.dataclass(frozen=True)
class DropConstraint:
    constraint_name: str

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"DROP CONSTRAINT {self.constraint_name}")

    def alter(self, table: MigrationStateTable):
        new_constraints = copy.copy(table.constraints)
        new_constraints.pop(self.constraint_name)
        return dataclasses.replace(table, constraints=new_constraints)


@dataclasses.dataclass(frozen=True)
class AddIndex:
    table_name: (str, str)
    index_name: str
    index: "MigrationIndex"

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder(dml_mode=True)

        unique = ""
        if self.index.unique:
            unique = "UNIQUE "

        concurrently = ""
        if self.index.concurrently:
            concurrently = "CONCURRENTLY "

        builder.write(
            f"CREATE {unique}INDEX {concurrently}{self.index_name} ON {self.table_name[1]} {self.index.on}"
        )
        await conn.execute(builder.q)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        tables = copy.copy(state.tables)
        table = state.tables[self.table_name]
        new_indexes = copy.copy(table.indexes)
        new_indexes[self.index_name] = self.index
        new_table = dataclasses.replace(table, indexes=new_indexes)
        tables[self.table_name] = new_table
        return dataclasses.replace(state, tables=tables)


@dataclasses.dataclass(frozen=True)
class RenameIndex:
    old_index_name: str
    index_name: str
    table_name: (str, str)

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder()
        builder.write(f"ALTER INDEX {self.old_index_name} RENAME TO {self.index_name}")
        await conn.execute(builder.q)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        tables = copy.copy(state.tables)
        table = state.tables[self.table_name]
        new_indexes = copy.copy(table.indexes)
        new_indexes[self.index_name] = new_indexes.pop(self.old_index_name)
        new_table = dataclasses.replace(table, indexes=new_indexes)
        tables[self.table_name] = new_table
        return dataclasses.replace(state, tables=tables)


@dataclasses.dataclass(frozen=True)
class DropIndex:
    table_name: (str, str)
    index_name: str

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder()
        builder.write(f"DROP INDEX {self.index_name}")
        await conn.execute(builder.q)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        tables = copy.copy(state.tables)
        table = state.tables[self.table_name]
        new_indexes = copy.copy(table.indexes)
        new_indexes.pop(self.index_name)
        tables[self.table_name] = dataclasses.replace(table, indexes=new_indexes)
        return dataclasses.replace(state, tables=tables)


@dataclasses.dataclass(frozen=True)
class AddReferencesConstraint:
    name: str
    constraint_name: str
    references: FrozenReference

    def __sql__(self, builder: SQLBuilder):
        builder.write(
            f"ADD CONSTRAINT {self.constraint_name} FOREIGN KEY ({self.name}) REFERENCES {self.references.table_name}"
        )

        if self.references.on_delete:
            builder.write(f" ON DELETE {self.references.on_delete}")

    def alter(self, table: MigrationStateTable):
        columns = copy.copy(table.columns)
        col = columns.pop(self.name)
        new_col = dataclasses.replace(col, references=self.references)
        columns[self.name] = new_col
        return dataclasses.replace(table, columns=columns)


AlterOperations = (
    DropColumn
    | CreateColumn
    | SetDefault
    | DropDefault
    | AddReferencesConstraint
    | DropConstraint
    | AddConstraint
    | AlterTypeUsing
)


@dataclasses.dataclass(kw_only=True)
class MigrationIndex:
    on: str
    unique: bool = True
    concurrently: bool = True

    @classmethod
    def from_index(cls, idx: Index):
        builder = SQLBuilder(dml_mode=True)
        builder.write("(")
        if isinstance(idx.on, tuple):
            on_cols = idx.on
        else:
            on_cols = [idx.on]
        wrote_val = False
        for on in on_cols:
            if wrote_val:
                builder.write(", ")
            wrote_val = True
            on.__sql__(builder)
        builder.write(")")
        if builder.vars:
            raise RhubarbException(
                f"Cannot use variables when defining Index {builder.q} {builder.vars}"
            )
        on_str = builder.q
        return cls(
            on=on_str,
            unique=idx.unique,
            concurrently=idx.concurrently,
        )


@dataclasses.dataclass(kw_only=True)
class MigrationConstraint:
    check: str
    unique: bool = False
    primary_key: bool = False

    @property
    def modifier(self):
        if self.primary_key:
            return "PRIMARY KEY"
        elif self.unique:
            return "UNIQUE"
        else:
            return "CHECK"

    @classmethod
    def from_constraint(cls, cst: Constraint):
        builder = SQLBuilder(dml_mode=True)
        cst.check.__sql__(builder)
        if builder.vars:
            raise RhubarbException(
                f"Cannot use variables when defining Constraint {builder.q} {builder.vars}"
            )
        check_str = builder.q
        return cls(check=check_str, unique=cst.unique)


@register_operation
@dataclasses.dataclass(frozen=True)
class CreateTable(MigrationOperation):
    schema: str
    name: str
    class_name: str
    primary_key: tuple[str, ...]
    columns: list[CreateColumn]
    constraints: dict[str, MigrationConstraint] = dataclasses.field(
        default_factory=dict
    )
    indexes: dict[str, MigrationIndex] = dataclasses.field(default_factory=dict)

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder(dml_mode=True)
        builder.write(f"CREATE TABLE {self.name} (")
        wrote_val = False
        for column in self.columns:
            if wrote_val:
                builder.write(", ")
            wrote_val = True
            builder.write(f"{column.name} {column.type.sql}")
            if column.type.optional:
                builder.write(" NULL")
            else:
                builder.write(" NOT NULL")
            if not isinstance(column.default, Unset) and not isinstance(
                column.default, Unset
            ):
                default = column.default
                if isinstance(default, str):
                    builder.write(f" DEFAULT {default}")
                else:
                    builder.write(f" DEFAULT ")
                    builder.write_value(default, column.type)

            if column.references:
                constraint_name = column.references.compute_constraint_name(column.name)
                builder.write(
                    f" CONSTRAINT {constraint_name} REFERENCES {column.references.table_name}"
                )

                if column.references.on_delete:
                    builder.write(f" ON DELETE {column.references.on_delete}")

        for constraint_name, constraint in self.constraints.items():
            if wrote_val:
                builder.write(", ")
            wrote_val = True
            builder.write(
                f"CONSTRAINT {constraint_name} {constraint.modifier} ({constraint.check})"
            )

        builder.write(f")")
        await conn.execute(builder.q)

        for index_name, index in self.indexes.items():
            builder = SQLBuilder()
            unique = ""
            if index.unique:
                unique = "UNIQUE "

            concurrently = ""
            if index.concurrently and conn.autocommit:
                concurrently = "CONCURRENTLY "

            builder.write(
                f"CREATE {unique}INDEX {concurrently}{index_name} ON {self.name} {index.on}"
            )
            await conn.execute(builder.q)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        new_table = MigrationStateTable(
            schema=self.schema,
            name=self.name,
            class_name=self.class_name,
            primary_key=self.primary_key,
            columns={},
            constraints=self.constraints,
            indexes=self.indexes,
        )

        tables = copy.copy(state.tables)
        tables[(self.schema, self.name)] = new_table
        return dataclasses.replace(state, tables=state.tables)


@register_operation
@dataclasses.dataclass(frozen=True)
class DropTable(MigrationOperation):
    schema: str
    name: str

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        tables = copy.copy(state.tables)
        tables.pop((self.schema, self.name))
        return dataclasses.replace(state, tables=state.tables)

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        await conn.execute(f"DROP TABLE {self.name}")


@register_operation
@dataclasses.dataclass(frozen=True)
class RenameTable(MigrationOperation):
    schema: str
    old_name: str
    new_name: str
    new_class_name: str

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder()
        builder.write(f'ALTER TABLE "{self.name}" RENAME TO {self.new_name}')
        await conn.execute(builder.q)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        tables = copy.copy(state.tables)
        old_table = tables.pop((self.schema, self.old_name))
        new_table = dataclasses.replace(
            old_table, name=self.new_name, class_name=self.new_class_name
        )
        tables[(self.schema, new_table.name)] = new_table
        return dataclasses.replace(state, tables=tables)


@register_operation
@dataclasses.dataclass(frozen=True)
class RenameColumn(MigrationOperation):
    schema: str
    name: str
    old_column_name: str
    new_column_name: str
    new_python_name: str

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder()
        builder.write(
            f'ALTER TABLE "{self.name}" RENAME COLUMN {self.old_column_name} TO {self.new_column_name}'
        )
        await conn.execute(builder.q)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        tables = copy.copy(state.tables)
        old_table = tables.pop((self.schema, self.old_name))
        columns = copy.deepcopy(old_table.columns)
        col = columns.pop(self.old_column_name)

        new_col = dataclasses.replace(
            col, name=self.new_column_name, python_name=self.new_python_name
        )
        columns[self.new_column_name] = new_col
        new_table = dataclasses.replace(old_table, columns=columns)
        tables[(self.schema, new_table.name)] = new_table
        return dataclasses.replace(state, tables=tables)


@register_operation
@dataclasses.dataclass(frozen=True)
class AlterTable(MigrationOperation):
    schema: str
    name: str
    alter_operations: list[AlterOperations]

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder()
        builder.write(f'ALTER TABLE "{self.name}" ')
        wrote_val = False
        for op in self.alter_operations:
            if wrote_val:
                builder.write(", ")
            wrote_val = True
            op.__sql__(builder)
        await conn.execute(builder.q)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        new_tables = copy.copy(state.tables)
        old_table = new_tables.pop((self.schema, self.name))

        for op in self.alter_operations:
            old_table = op.alter(old_table)

        new_tables[(self.schema, old_table.name)] = old_table
        return dataclasses.replace(state, tables=new_tables)


@register_operation
@dataclasses.dataclass(frozen=True)
class SetMeta(MigrationOperation):
    new_meta_kvs: dict[str, Any]

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        pass

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        new_meta = copy.copy(state.meta)
        new_meta.update(self.new_meta_kvs)
        return dataclasses.replace(state, meta=new_meta)


@dataclasses.dataclass
class MigrationInfo:
    state: MigrationStateDatabase
    conn: AsyncConnection
    _model_cache: dict[(str, str), Type[SqlModel]] = dataclasses.field(
        default_factory=dict
    )

    def get_model(self, table_name: str, schema="public") -> Type[T]:
        if (schema, table_name) not in self._model_cache:
            table = self.state.tables[(schema, table_name)]
            data_class = dataclasses.make_dataclass(
                table.class_name,
                [
                    (c.python_name, c.type.to_python(), c.as_column_field())
                    for c in table.columns.values()
                ],
                kw_only=True,
            )

            data_class = type(table.class_name, (data_class,), {})

            if len(table.primary_key) == 1:
                data_class.__pk__ = table.primary_key[0]
            else:
                data_class.__pk__ = table.primary_key
            data_class.__schema__ = table.schema
            data_class.__table__ = table.name
            self._model_cache[(schema, table_name)] = table_decorator(data_class)

        return self._model_cache[(schema, table_name)]


@register_operation
@dataclasses.dataclass(frozen=True)
class RunPython(MigrationOperation):
    python_function: Callable[[MigrationInfo], Optional[Awaitable[None]]]

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        result = self.python_function(MigrationInfo(state=state, conn=conn))
        if inspect.isawaitable(result):
            result = await result
        return result

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        return state


@register_operation
@dataclasses.dataclass(frozen=True)
class RawSQL(MigrationOperation):
    sql: str

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        await conn.execute(self.sql)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        return state


@dataclasses.dataclass(frozen=True)
class Migration:
    id: str
    depends_on: list[str]
    operations: list[MigrationOperation]
    atomic: bool = True
