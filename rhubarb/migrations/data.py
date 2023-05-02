import copy
import inspect
import json
import pprint
from typing import Callable, Type, Any, Awaitable, Optional
from rhubarb.core import SupportsSqlModel, T, UNSET, DEFAULT_SQL_FUNCTION, Unset
from rhubarb.object_set import SQLBuilder, SqlType, DEFAULT_REGISTRY, ColumnField, column, columns, pk_column_names
from rhubarb.object_set import table as table_decorator
import dataclasses
from psycopg import AsyncConnection


@dataclasses.dataclass
class MigrationStateColumn:
    name: str
    python_name: str
    type: SqlType
    default: DEFAULT_SQL_FUNCTION | None = None

    def as_column_field(self) -> ColumnField:
        return column(
            virtual=False,
            column_name=self.name,
            python_name=self.python_name,
        )


@dataclasses.dataclass
class MigrationStateTable:
    schema: str
    name: str
    class_name: str
    primary_key: tuple[str, ...]
    columns: dict[str, MigrationStateColumn]
    constraints: dict[str, str] = dataclasses.field(default_factory=dict)
    indexes: dict[str, "Index"] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class MigrationStateDatabase:
    tables: dict[(str, str), MigrationStateTable] = dataclasses.field(default_factory=dict)
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
        )
    pk = tuple(pk_column_names(m))
    schema = m.__schema__
    name = m.__table__
    pks = ", ".join(pk)
    constraints = {f"{name}_pk": f"PRIMARY KEY ({pks})"}
    return MigrationStateTable(
        schema=schema,
        name=name,
        primary_key=pk,
        columns=cols,
        class_name=m.__name__,
        constraints=constraints,
    )


class MigrationJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            dict_vals = dataclasses.asdict(o)
            return dict(
                {"_operation": o.__class__.__name__}.items() | dict_vals.items()
            )
        elif isinstance(o, Unset):
            return "...cgda.UNSET"

        return super().default(o)


@register_operation
@dataclasses.dataclass
class MigrationOperation:
    def __as_py__(self) -> str:
        param_str = "\n               ".join(pprint.pformat(self).split("\n"))
        return f"            {param_str}"

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        raise NotImplementedError

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        raise NotImplementedError


@dataclasses.dataclass
class AlterOperation:
    def __sql__(self, table: MigrationStateTable) -> MigrationStateDatabase:
        pass

    def alter(self, table: MigrationStateTable) -> MigrationStateDatabase:
        pass


@dataclasses.dataclass
class CreateColumn(AlterOperation):
    name: str
    python_name: str
    type: SqlType
    default: DEFAULT_SQL_FUNCTION | None = None

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"ADD COLUMN {self.name} {self.type.raw_sql}")
        if self.type.optional:
            builder.write(" NULL")
        else:
            builder.write(" NOT NULL")

        if self.default:
            builder.write(f" DEFAULT {self.default}")

    def alter(self, table: MigrationStateTable) -> MigrationStateTable:
        table.columns[self.name] = MigrationStateColumn(
            name=self.name,
            type=self.type,
            default=self.default,
            python_name=self.python_name,
        )
        return table


@dataclasses.dataclass
class DropColumn:
    name: str

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"DROP COLUMN {self.name}")

    def alter(self, table):
        table.columns.pop(self.name)
        return table


@dataclasses.dataclass
class AlterTypeDefault:
    name: str
    new_type: SqlType
    using: str | None = None

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"ALTER {self.name} TYPE ")
        self.new_type.__sql__(builder)
        if self.using:
            builder.write(f"USING {self.using}")

    def alter(self, table):
        col = table.columns.pop(self.name)
        new_col = copy.deepcopy(col)
        new_col.type = self.new_type
        table.columns[self.name] = new_col
        return table


@dataclasses.dataclass
class SetDefault:
    name: str
    default: DEFAULT_SQL_FUNCTION | None = None

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"ALTER {self.name} SET DEFAULT {self.default}")

    def alter(self, table):
        col = table.columns.pop(self.name)
        new_col = copy.deepcopy(col)
        new_col.default = self.default
        table.columns[self.name] = new_col
        return table


@dataclasses.dataclass
class DropDefault:
    name: str

    def __sql__(self, builder: SQLBuilder):
        builder.write(f"ALTER {self.name} DROP DEFAULT")

    def alter(self, table):
        col = table.columns.pop(self.name)
        new_col = copy.deepcopy(col)
        new_col.default = UNSET
        table.columns[self.name] = new_col
        return table


AlterOperations = DropColumn | CreateColumn | SetDefault | DropDefault


@dataclasses.dataclass(kw_only=True)
class Index:
    on: str
    unique: bool = True
    concurrently: bool = True


@register_operation
@dataclasses.dataclass
class CreateTable(MigrationOperation):
    schema: str
    name: str
    class_name: str
    primary_key: tuple[str, ...]
    columns: list[CreateColumn]
    constraints: dict[str, str] = dataclasses.field(default_factory=dict)
    indexes: dict[str, Index] = dataclasses.field(default_factory=dict)

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder()
        builder.write(f"CREATE TABLE {self.name} (")
        wrote_val = False
        for column in self.columns:
            if wrote_val:
                builder.write(", ")
            wrote_val = True
            builder.write(f"{column.name} {column.type.raw_sql}")
            if column.type.optional:
                builder.write(" NULL")
            else:
                builder.write(" NOT NULL")
            if column.default and not isinstance(column.default, Unset):
                builder.write(f" DEFAULT {column.default}")

        for constraint_name, constraint in self.constraints.items():
            if wrote_val:
                builder.write(", ")
            wrote_val = True
            builder.write(f"CONSTRAINT {constraint_name} {constraint}")

        builder.write(f")")
        print(builder.q)
        await conn.execute(builder.q)

        for index_name, index in self.indexes.items():
            builder = SQLBuilder()
            unique = ""
            if index.unique:
                unique = "UNIQUE"

            concurrently = ""
            if index.concurrently:
                concurrently = "CONCURRENTLY"

            builder.write(
                f"CREATE {unique} INDEX {concurrently} {index_name} ON {self.name} ({index.on})"
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
        for col in self.columns:
            new_table = col.alter(new_table)

        state.tables[(self.schema, self.name)] = new_table
        return state


@register_operation
@dataclasses.dataclass
class DropTable(MigrationOperation):
    schema: str
    name: str

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        state.tables.pop((self.schema, self.name))
        return state


@register_operation
@dataclasses.dataclass
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
        old_table = state.tables.pop((self.schema, self.old_name))
        new_table = copy.deepcopy(old_table)
        new_table.name = self.new_name
        new_table.class_name = self.new_class_name
        state.tables[(self.schema, new_table.name)] = new_table
        return state


@register_operation
@dataclasses.dataclass
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
        old_table = state.tables.pop((self.schema, self.old_name))
        new_table = copy.deepcopy(old_table)
        col = new_table.columns.pop(self.old_column_name)
        col.name = self.new_column_name
        col.python_name = self.new_python_name
        new_table.columns[self.new_column_name] = col
        state.tables[(self.schema, new_table.name)] = new_table
        return state


@register_operation
@dataclasses.dataclass
class AlterTable(MigrationOperation):
    schema: str
    name: str
    alter_operations: list[AlterOperations]

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        builder = SQLBuilder()
        builder.write(f'ALTER TABLE "{self.name}"')
        for op in self.alter_operations:
            op.__sql__(builder)
        await conn.execute(builder.q)

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        old_table = state.tables.pop((self.schema, self.name))
        new_table = copy.deepcopy(old_table)

        for op in self.alter_operations:
            new_table = op.alter(new_table)

        state.tables[(self.schema, new_table.name)] = new_table
        return state


@register_operation
@dataclasses.dataclass
class SetMeta(MigrationOperation):
    new_meta_kvs: dict[str, Any]

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        pass

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        new_meta = copy.copy(state.meta)
        new_meta.update(self.new_meta_kvs)
        state.meta = new_meta
        return state


@dataclasses.dataclass
class MigrationInfo:
    state: MigrationStateDatabase
    conn: AsyncConnection
    _model_cache: dict[(str, str), Type[SupportsSqlModel]] = dataclasses.field(
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
@dataclasses.dataclass
class RunPython(MigrationOperation):
    python_function: Callable[[MigrationInfo], Optional[Awaitable[None]]]

    async def run(self, state: MigrationStateDatabase, conn: AsyncConnection):
        result = self.python_function(MigrationInfo(state=state, conn=conn))
        if inspect.isawaitable(result):
            result = await result
        return result

    def forward(self, state: MigrationStateDatabase) -> MigrationStateDatabase:
        return state


@dataclasses.dataclass
class Migration:
    id: str
    depends_on: list[str]
    operations: list[MigrationOperation]
