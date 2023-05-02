from __future__ import annotations

import asyncio
import copy
import dataclasses
import datetime
import functools
import inspect
import time
import uuid
from collections import defaultdict
from typing import TypeVar, Generic, Iterator, Literal, Type, Optional, Self, Any, Sequence, overload, Callable, \
    Mapping, Union, TYPE_CHECKING, Awaitable

import strawberry
from psycopg import Connection, AsyncConnection
from psycopg.rows import dict_row
from strawberry.annotation import StrawberryAnnotation
from strawberry.type import StrawberryOptional, StrawberryType, StrawberryList
from strawberry.types import Info
from strawberry.types.fields.resolver import StrawberryResolver
from strawberry.types.nodes import SelectedField, FragmentSpread, InlineFragment

from rhubarb.core import T, V, SupportsSqlModel, J, UNSET, DEFAULT_SQL_FUNCTION, new_ref_id, SQLValue, \
    default_function_to_python
from rhubarb.errors import RhubarbException
from strawberry.field import StrawberryField
from strawberry.types.types import TypeDefinition
from strawberry.scalars import JSON

SelectedFields = list[SelectedField | FragmentSpread | InlineFragment]


@dataclasses.dataclass(kw_only=True)
class SqlType:
    raw_sql: str
    optional: bool = False
    python_type: Optional[type] = None

    def __sql__(self, builder: SQLBuilder):
        builder.write(self.raw_sql)

    def to_python(self) -> Type:
        if self.python_type:
            return self.python_type
        match self.raw_sql:
            case "BIGINT":
                return int
            case "FLOAT":
                return float
            case "TEXT":
                return str
            case "BYTEA":
                return bytes
            case "TIMESTAMPTZ":
                return datetime.datetime
            case "DATE":
                return datetime.date
            case "UUID":
                return uuid.UUID
            case "JSONB":
                return JSON
            case other:
                raise RhubarbException(f"Cannot find python type for {other}")

    @classmethod
    def from_string(cls, s: str, optional=False):
        return cls(s)

    @classmethod
    def from_python(cls, t: StrawberryType | type):
        if hasattr(t, "__sql_type__"):
            return t.__sql_type__()
        elif isinstance(t, StrawberryOptional):
            inner_type = cls.from_python(t.of_type)
            inner_type.optional = True
            return inner_type
        elif issubclass(t, int):
            return cls(raw_sql="BIGINT")
        elif issubclass(t, float):
            return cls(raw_sql="FLOAT")
        elif issubclass(t, str):
            return cls(raw_sql="TEXT")
        elif issubclass(t, bytes):
            return cls(raw_sql="BYTEA")
        elif issubclass(t, datetime.datetime):
            return cls(raw_sql="TIMESTAMPTZ")
        elif issubclass(t, datetime.date):
            return cls(raw_sql="DATE")
        elif issubclass(t, uuid.UUID):
            return cls(raw_sql="UUID")
        elif issubclass(t, JSON):
            return cls(raw_sql="JSONB")
        raise RhubarbException(
            f"InvalidSQL Type: {t} cannot be made into a valid SQLType"
        )

    def __repr__(self):
        return f"SqlType(raw_sql='{self.raw_sql}', optional={self.optional})"


class SQLBuilder:
    def __init__(self):
        self.q = ""
        self.vars = []
        self.column_mappings: dict[str, str] = {}
        self.alias_count = 0
        self.wrote_alias = False
        self.writing_subquery = False

    def write(self, s: str):
        self.q += s

    def next_alias(self) -> int:
        self.alias_count += 1
        return self.alias_count

    def write_column(self, reference: ModelReference, field: ColumnField, alias: str = "col") -> str:
        column_name = f'{reference.alias()}."{field.column_name}"'
        if column_name in self.column_mappings:
            return self.column_mappings[column_name]

        self.start_selection()
        self.write(column_name)
        new_alias = self.write_alias(alias_base=(alias or field.column_name))
        self.column_mappings[column_name] = new_alias
        return new_alias

    def start_selection(self):
        if self.wrote_alias:
            self.write(", ")

    def write_alias(self, alias_base=None) -> str:
        alias_base = alias_base or "col"
        self.wrote_alias = True
        if self.writing_subquery:
            alias = alias_base
        else:
            alias = f"{alias_base}_{self.next_alias()}".lower()
        self.write(f" AS {alias}")
        return alias

    def write_value(self, v: Any):
        if hasattr(v, "__sql__"):
            v.__sql__(self)
        else:
            sql_type = SqlType.from_python(type(v))
            self.write(f"%s::{sql_type.raw_sql}")
            self.vars.append(v)


def call_with_maybe_info(f, obj, info):
    sig = inspect.signature(f)
    if len(sig.parameters) == 1:
        return f(obj)
    else:
        return f(obj, info)


def write_single_or_tuple(
    clauses: tuple[Selector, ...] | Selector, builder: SQLBuilder
):
    if isinstance(clauses, tuple):
        wrote_last = False
        for clause in clauses:
            if wrote_last:
                builder.write(", ")
            builder.write_value(clause)
            wrote_last = True
    else:
        builder.write_value(clauses)


JOIN_TYPES = Literal["LEFT", "INNER"]


@dataclasses.dataclass
class Join(Generic[T, J]):
    id: str
    model_reference: ModelReference[J]
    on: Selector[bool]
    object_set: ObjectSet[T, ModelSelector[T]] | None
    join_type: JOIN_TYPES

    def __hash__(self):
        return self.id.__hash__()

    def __sql__(self, builder: SQLBuilder, join_fields: set[str] = None):
        if self.object_set is None:
            self.model_reference.__sql__(builder)
        else:
            builder.writing_subquery = True
            builder.write("(")
            self.object_set.__sql__(builder, join_fields)
            builder.write(")")
            builder.writing_subquery = False


@dataclasses.dataclass
class ModelReference(Generic[T]):
    id: str
    model: Type[T]
    object_set: ObjectSet[T, ModelSelector[T]] | None

    def __repr__(self):
        return f"ModelReference({self.model.__name__}, {self.id})"

    @classmethod
    def new(
        cls,
        model: Type[T],
        object_set: ObjectSet[T, ModelSelector[T]] | None,
        reference_id: str | None = None,
    ):
        reference_id = reference_id or new_ref_id()
        mid = f"{model.__name__.lower()}_{reference_id}"
        return cls(id=mid, model=model, object_set=object_set)

    def alias(self) -> str:
        return f"{self.id}"

    def __sql__(self, builder: SQLBuilder):
        schema_name = self.model.__schema__
        table_name = self.model.__table__

        builder.write(f'"{schema_name}"."{table_name}"')


class Extractor(Generic[V]):
    def __init__(self, model_reference: ModelReference, field: StrawberryField[V]):
        self.model_reference = model_reference
        self.field = field

    def __repr__(self):
        return f"{self.__class__.__name__}({self.model_reference}, {self.field and self.field.name})"

    async def extract(self, row) -> V:
        raise NotImplementedError

    def for_field(self, model_reference: ModelReference, field: StrawberryField[V]) -> Optional[Self]:
        if self.model_reference is None or self.field is None:
            return None

        if self.model_reference.id == model_reference.id and self.field.name == field.name:
            print("Found!", self.model_reference.model, self.field.name)
            return self
        else:
            return None

    def reset_cache(self):
        return {}

    def add_to_cache(self, cache, k, v):
        cache[k] = v

    def unwrap(self):
        return self


class ListExtractor(Extractor[list[V]]):
    def __init__(self, inner_extractor: Extractor[V], model_reference: ModelReference, field: StrawberryField[V]):
        self.inner_extractor = inner_extractor
        super().__init__(model_reference, field)

    async def extract(self, row) -> list[V]:
        return await self.inner_extractor.extract(row)

    def unwrap(self):
        return self.inner_extractor.unwrap()

    def for_field(self, model_reference: ModelReference, field: StrawberryField[V]) -> Optional[Self]:
        if found := super().for_field(model_reference, field):
            return found
        return self.inner_extractor.for_field(model_reference, field)

    def reset_cache(self):
        return defaultdict(list)

    def add_to_cache(self, cache, k, v):
        cache[k].append(v)


class SimpleExtractor(Extractor[V]):
    def __init__(self, alias: str, model_reference: ModelReference, field: StrawberryField[V] | None):
        self.alias = alias
        super().__init__(model_reference, field)

    async def extract(self, row) -> V:
        return row[self.alias]


class WrappedExtractor(Extractor[V]):
    def __init__(self, extractor: Extractor[V], model_reference: ModelReference, field: StrawberryField[V] | None):
        self.extractor = extractor
        super().__init__(model_reference, field)

    def reset_cache(self):
        return self.extractor.reset_cache()

    def add_to_cache(self, cache, k, v):
        return self.extractor.add_to_cache(cache, k, v)

    async def extract(self, row) -> V:
        return await self.extractor.extract(row)

    def for_field(self, model_reference: ModelReference, field: StrawberryField[V]) -> Optional[Self]:
        if extractor := super().for_field(model_reference, field):
            return extractor
        return self.extractor.for_field(model_reference, field)

    def unwrap(self):
        return self.extractor.unwrap()


class ModelExtractor(Extractor[V]):
    def __init__(
        self,
        model: dataclasses.dataclass,
        field_aliases: dict[str, (ColumnField, Extractor)],
        model_reference: ModelReference | None,
        field: StrawberryField[V] | None,
    ):
        self.model = model
        self.field_aliases = field_aliases
        super().__init__(model_reference, field)

    def add_to_cache(self, cache, k, v):
        if not hasattr(v, "__pk__"):
            v._cached_pk = k
        return super().add_to_cache(cache, k, v)

    async def extract(self, row) -> V:
        field_names = {f.name for f in dataclasses.fields(self.model) if f.init}
        kwargs = {
            k: await selector.extract(row)
            for k, (col_field, selector) in self.field_aliases.items()
            if k in field_names
        }
        for k in field_names:
            if k not in kwargs:
                kwargs[k] = UNSET
        return self.model(**kwargs)

    def for_field(self, model_reference: ModelReference, field: StrawberryField[V]) -> Optional[Self]:
        if found := super().for_field(model_reference, field):
            return found
        for _, field_extractor in self.field_aliases.values():
            if found := field_extractor.for_field(model_reference, field):
                return found

    def sub_extractor(self, fn: str) -> Optional[Extractor]:
        if field := self.field_aliases.get(fn):
            return field[1]


class ModelWrapper:
    def __init__(self, model, set_fields):
        self._model = model
        self._set_fields = set_fields

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            set_fields = self._set_fields
            if item in set_fields:
                return set_fields[item]
            return getattr(self._model, item)


class DictExtractor(Extractor[V]):
    def __init__(
        self, key_aliases: dict[str, Extractor], model_reference: ModelReference | None, field: StrawberryField[V] | None
    ):
        self.key_aliases = key_aliases
        super().__init__(model_reference, field)

    async def extract(self, row) -> dict[str, SQLValue]:
        return {k: await v.extract(row) for k, v in self.key_aliases.items()}

    def for_field(self, model_reference: ModelReference, field: StrawberryField[V]) -> Optional[Self]:
        if found := super().for_field(model_reference, field):
            return found
        for field_extractor in self.key_aliases.values():
            if found := field_extractor.for_field(model_reference, field):
                return found


class TupleExtractor(Extractor[V]):
    def __init__(
        self, tuple_aliases: Sequence[Extractor, ...], model_reference: ModelReference | None, field: StrawberryField[V] | None
    ):
        self.tuple_aliases = tuple_aliases
        super().__init__(model_reference, field)

    async def extract(self, row) -> tuple[SQLValue, ...]:
        return tuple(await v.extract(row) for v in self.tuple_aliases)

    def for_field(self, model_reference: ModelReference, field: StrawberryField[V]) -> Optional[Self]:
        if found := super().for_field(model_reference, field):
            return found
        for field_extractor in self.tuple_aliases:
            if found := field_extractor.for_field(model_reference, field):
                return found


class Selector(Generic[V]):
    def __joins__(self) -> Iterator[(str, Join, str)]:
        return iter(())

    def __sql__(self, builder: SQLBuilder):
        raise NotImplementedError(f"NotImplementedError: {self}")

    def __extractor__(self, builder: SQLBuilder, alias_name: str = None) -> Extractor:
        builder.start_selection()
        self.__sql__(builder)
        alias = builder.write_alias(alias_name)
        return SimpleExtractor(alias, None, None)

    def __model_reference__(self) -> Optional[ModelReference]:
        return None

    def __field__(self) -> Optional[StrawberryField]:
        return None

    def __inner_selector__(self) -> Selector:
        return self

    def __infix(self, other, op, reverse_args=False):
        return Computed(
            args=[other, self] if reverse_args else [self, other],
            op=op,
            infixed=True,
        )

    def __contains__(self, other):
        return self.__infix(other, "IN", reverse_args=True)

    def __eq__(self, other):
        return self.__infix(other, "=")

    def __ne__(self, other):
        return self.__infix(other, "<>")

    def __gt__(self, other):
        return self.__infix(other, ">")

    def __ge__(self, other):
        return self.__infix(other, ">=")

    def __lt__(self, other):
        return self.__infix(other, "<")

    def __le__(self, other):
        return self.__infix(other, "<=")

    def __or__(self, other):
        return self.__infix(other, "OR")

    def __and__(self, other):
        return self.__infix(other, "AND")

    def __add__(self, other):
        return self.__infix(other, "+")

    def __sub__(self, other):
        return self.__infix(other, "-")

    def __div__(self, other):
        return self.__infix(other, "/")

    def __mul__(self, other):
        return self.__infix(other, "*")

    def __pow__(self, other):
        return self.__infix(other, "^")


class WrappedSelector(Selector[V]):
    def __init__(self, selector: Selector[V], model_reference: ModelReference, field: StrawberryField[V] | None):
        self._selector = selector
        self._model_reference = model_reference
        self._field = field

    def __repr__(self):
        return f"WrappedSelector({self._selector}, {self._model_reference.model.__name__}.{self._field.name})"

    def __joins__(self) -> Iterator[(str, Join, str)]:
        return self._selector.__joins__()

    def __joins__(self) -> Iterator[(str, Join, str)]:
        if (
            isinstance(self._selector, Aggregate)
            and self._selector._model_selector._join
        ):
            join = self._selector._model_selector._join
            yield join.id, join, self._field.name
        else:
            yield from self._selector.__joins__()


    def __sql__(self, builder: SQLBuilder):
        return self._selector.__sql__(builder)

    def __extractor__(self, builder: SQLBuilder, alias_name: str = None) -> Extractor:
        if (
            isinstance(self._selector, Aggregate)
            and self._selector._model_selector._join
        ):
            return ColumnSelector(
                self._selector._model_selector._model_reference,
                self._field,
                self._selector._model_selector._join,
            ).__extractor__(builder, alias_name or self._field.name)
        extractor = self._selector.__extractor__(builder, alias_name or self._field.name)
        return WrappedExtractor(extractor, model_reference=self._model_reference, field=self._field)

    def __model_reference__(self) -> Optional[ModelReference]:
        # if self._selector.__field__():
        #     return self._selector.__model_reference__()
        return self._model_reference

    def __field__(self) -> Optional[StrawberryField]:
        # return self._selector.__field__() or self._field
        return self._field

    def __inner_selector__(self) -> Selector:
        return self._selector.__inner_selector__()

    def __getattribute__(self, item):
        if item.startswith("_"):
            return object.__getattribute__(self, item)
        selector = self._selector
        return getattr(self._selector, item)

# class WildCardSelector(Selector[V]):
#     def __init__(self, model_reference: ModelReference):
#         self._model_reference = model_reference
#
#     def __sql__(self, builder: SQLBuilder):
#         builder.start_selection()
#         builder.write(f"{self._model_reference.alias()}.*")
#
#     def __extractor__(self, builder: SQLBuilder) -> Extractor:
#         self.__sql__(builder)
#         return SimpleExtractor(None, None, None)
#

# class GQLFieldWrappedSelector(Selector[V]):
#     def __init__(
#         self,
#         selector: Selector[V],
#         field: StrawberryField[V],
#         # model: Type[SupportsSqlModel],
#         model_reference: ModelReference,
#     ):
#         self.selector = selector
#         self.field = field
#         self._model_reference = model_reference
#
#     def __model_reference__(self) -> Optional[ModelReference]:
#         return self._model_reference
#
#     def __inner_selector__(self) -> Selector:
#         return self.selector
#
#     def __sql__(self, builder: SQLBuilder):
#         return self.selector.__sql__(builder)
#
#     def __extractor__(self, builder: SQLBuilder, alias: str = None) -> Extractor:
#         if (
#             isinstance(self.selector, Aggregate)
#             and self.selector._model_selector._join
#         ):
#             return ColumnSelector(
#                 self.selector._model_selector._model_reference,
#                 self.field,
#                 self.selector._model_selector._join,
#             ).__extractor__(builder, alias)
#         return self.selector.__extractor__(builder, alias)
#
#     def __joins__(self) -> Iterator[(str, Join, str)]:
#         if (
#             isinstance(self.selector, Aggregate)
#             and self.selector._model_selector._join
#         ):
#             join = self.selector._model_selector._join
#             yield join.id, join, self.field.name
#         else:
#             yield from self.selector.__joins__()
#

class Computed(Selector[V]):
    def __init__(self, args: list[Selector], op: str, infixed=True):
        self._args = args
        self._op = op
        self._infixed = infixed

    def __sql__(self, builder: SQLBuilder):
        if self._infixed:
            builder.write(f"(")
            builder.write_value(self._args[0])
            builder.write(f" {self._op} ")
            builder.write_value(self._args[1])
            builder.write(f")")
        else:
            builder.write(f"{self._op}(")
            wrote_val = False
            for arg in self._args:
                if wrote_val:
                    builder.write(", ")
                wrote_val = True
                builder.write_value(arg)
            builder.write(")")

    def __joins__(self) -> Iterator[(str, Join, str)]:
        for arg in self._args:
            if hasattr(arg, "__joins__"):
                yield from arg.__joins__()


class Value(Selector[V]):
    def __init__(self, val: Any):
        self.val = val

    def __sql__(self, builder: SQLBuilder):
        builder.write_value(self.val)

    def __joins__(self) -> Iterator[(str, Join, str)]:
        if hasattr(self.val, "__joins__"):
            yield from self.val.__joins__()


class PythonValueExtractor(Extractor[V]):
    def __init__(self, value: V, model_reference: ModelReference | None, field: StrawberryField | None):
        self.value = value
        super().__init__(model_reference, field)

    async def extract(self, row) -> V:
        return self.value


class PythonOnlyValue(Selector[V]):
    def __init__(self, val: Any):
        self.val = val

    def __sql__(self, builder: SQLBuilder):
        pass

    def __extractor__(self, builder: SQLBuilder, alias_name: str = None) -> Extractor:
        return PythonValueExtractor(self.val, None, None)

    def __joins__(self) -> Iterator[(str, Join, str)]:
        if hasattr(self.val, "__joins__"):
            yield from self.val.__joins__()


class UseExtractor(Extractor[V]):
    def __init__(self, fn: Callable[..., V | Awaitable[V]], dependencies: list[Extractor], kw_dependencies: dict[str, Extractor], model_reference: ModelReference | None, field: StrawberryField | None):
        self.fn = fn
        self.dependencies = dependencies
        self.kw_dependencies = kw_dependencies
        super().__init__(model_reference, field)

    async def extract(self, row) -> V:
        dependencies = [await dep.extract(row) for dep in self.dependencies]
        kw_dependencies = {k: await dep.extract(row) for k, dep in self.kw_dependencies.items()}
        result = self.fn(*dependencies, **kw_dependencies)
        if inspect.isawaitable(result):
            result = await result
        return result


class UseSelector(Selector[V]):
    def __init__(self, fn: Callable[..., V | Awaitable[V]], dependencies: list[Selector[V]], kwarg_dependencies: dict[str, Selector]):
        self.fn = fn
        self.dependencies = dependencies
        self.kwarg_dependencies = kwarg_dependencies

    def __sql__(self, builder: SQLBuilder):
        raise RhubarbException("UseSelector cannot be used as SQL")

    def __extractor__(self, builder: SQLBuilder, alias_name: str = None) -> Extractor:
        dependant_extractors = [
            dep.__extractor__(builder) for dep in self.dependencies
        ]
        dependant_kwarg_extractors = {
            k: dep.__extractor__(builder) for k, dep in self.kwarg_dependencies.items()
        }
        return UseExtractor(self.fn, dependant_extractors, dependant_kwarg_extractors, None, None)

    def __joins__(self) -> Iterator[(str, Join, str)]:
        seen = set()
        for s in self.dependencies:
            yield from joins(s, seen=seen)

        for s in self.kwarg_dependencies.values():
            yield from joins(s, seen=seen)


class Aggregate(Computed[V]):
    def __init__(self, model_selector: ModelSelector, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_selector = model_selector


class ColumnSelector(Selector[V]):
    def __init__(
        self,
        model_reference: ModelReference,
        field: ColumnField,
        join: Join | None = None,
    ):
        self._model_reference = model_reference
        self._field = field
        self._join = join

    def __repr__(self):
        return f"ColumnSelector({self._model_reference.model.__name__}.{self._field.column_name})"

    def __model_reference__(self) -> Optional[ModelReference]:
        return self._model_reference

    def __field__(self) -> Optional[StrawberryField]:
        return self._field

    def __sql__(self, builder: SQLBuilder):
        builder.write(f'{self._model_reference.alias()}."{self._field.column_name}"')

    def __extractor__(self, builder: SQLBuilder, alias: str = None) -> Extractor:
        alias = builder.write_column(self._model_reference, self._field, alias=alias)
        return SimpleExtractor(alias, self._model_reference, self._field)

    def __joins__(self) -> Iterator[(str, Join, str)]:
        for join_id, join in self._model_reference.object_set.joins.items():
            for join_field in self._model_reference.object_set.join_fields[join_id]:
                yield join_id, join, join_field

        if self._join:
            yield self._join.id, self._join, self._field.name


class FieldSelector(Selector[V]):
    def __init__(
        self,
        model_selector: ModelSelector,
        field: StrawberryField,
        join: Join | None = None,
        selected_fields: SelectedFields = None
    ):
        self._field = field
        self._model_reference = model_selector._model_reference
        self._model_selector = model_selector
        self._selected_fields = selected_fields
        self._join = join

    def __model_reference__(self) -> Optional[ModelReference]:
        return self._model_reference

    def __sql__(self, builder):
        self().__sql__(builder)

    def __extractor__(self, builder: SQLBuilder, alias_name: str = None) -> Extractor:
        builder.start_selection()
        self.__sql__(builder)
        alias = builder.write_alias(alias_name or self._field.name)
        return SimpleExtractor(alias, self._model_reference, self._field)

    def __field__(self) -> Optional[StrawberryField]:
        return self._field

    def __call__(self, *args, **kwargs):
        source = self._model_selector
        field = self._field
        args = list(args)
        info = kwargs.pop("info", None)
        selection = get_result(field, source, info, args, kwargs)
        if isinstance(selection, Aggregate):
            if not hasattr(self._model_reference.model, "__group_by__"):
                raise RhubarbException(
                    f"Returned {self._field.name} returned an Aggregate function without a group by on {self._model_reference.model}"
                )
            if self._join is not None:
                selection = ColumnSelector(self._model_reference, field, self._join)

        selection = optimize_selection(self._selected_fields, selection)
        selection = WrappedSelector(selector=selection, model_reference=self._model_reference, field=self._field)
        return selection


class ModelSelector(Selector[T]):
    _extractor = ModelExtractor

    def __init__(
        self,
        model_reference: ModelReference[T],
        selected_fields: list[SelectedField] = None,
        join: Join | None = None,
    ):
        self._model_reference = model_reference
        self._selected_fields = selected_fields
        self._selected_lookup = {}

        if selected_fields is None:
            self._selection_names = {
                col.name for col in columns(self._model_reference.model, virtual=False)
            }
        else:
            self._selected_lookup = {
                f.name: f for f in selected_fields
            }
            self._selection_names = {
                f.name for f in selected_fields
            }
        self._selection_names |= pk_column_names(self._model_reference.model)
        self._columns = {}
        self._join = join

    def __repr__(self):
        return f"ModelSelector({self._model_reference}, {self._selection_names})"

    def __restrict__(self, selected_fields: SelectedFields) -> Self:
        return ModelSelector(
            model_reference=self._model_reference,
            selected_fields=selected_fields,
            join=self._join,
        )

    def __model_reference__(self) -> Optional[ModelReference]:
        return self._model_reference

    def _selector_for_field(self, column_field: StrawberryField, unwrap=False):
        if isinstance(column_field, ColumnField) and not column_field.virtual:
            selector = ColumnSelector(
                self._model_reference, column_field, self._join
            )
        else:
            if field_selection := self._selected_lookup.get(column_field.name):
                selected_fields = field_selection.selections
            else:
                selected_fields = None
            selector = FieldSelector(self, column_field, self._join, selected_fields=selected_fields)
            if unwrap:
                selector = selector(info=self._model_reference.object_set.info)
        return selector

    def __joins__(self) -> Iterator[(str, Join, str)]:
        seen = set()
        for column_field in columns(self._model_reference.model, inlinable=True):
            if column_field.name not in self._selection_names:
                continue
            selector = self._selector_for_field(column_field, unwrap=True)
            yield from joins(selector, seen=seen)

    def __sql__(self, builder: SQLBuilder):
        primary_key = pk_columns(self._model_reference.model)
        if isinstance(primary_key, tuple):
            builder.write("(")
            wrote_val = False
            for is_last, pk_field in primary_key:
                if wrote_val:
                    builder.write(", ")
                wrote_val = True
                selector = self._selector_for_field(pk_field)
                selector.__sql__(builder)

            builder.write(")")
        else:
            selector = self._selector_for_field(primary_key)
            selector.__sql__(builder)

    def __extractor__(
        self, builder: SQLBuilder, alias: str = None
    ) -> Extractor:
        model = self._model_reference.model
        column_aliases = {}
        for column_field in columns(self._model_reference.model, inlinable=True):
            if column_field.name not in self._selection_names:
                continue
            selector = self._selector_for_field(column_field, unwrap=True)
            extractor = selector.__extractor__(builder, column_field.name)
            column_aliases[column_field.name] = (column_field, extractor)
        return self._extractor(model, column_aliases, self._model_reference, None)

    def __getattribute__(self, item):
        if item.startswith("_"):
            return object.__getattribute__(self, item)
        else:
            reference: ModelReference = object.__getattribute__(
                self, "_model_reference"
            )
            model: SupportsSqlModel = reference.model
            type_def: TypeDefinition = model._type_definition

            if field := type_def.get_field(item):
                return self._selector_for_field(field)
            else:
                raise RhubarbException(f"Field {item} not found on {type_def.name}")


class DataclassSelector(Selector[T]):
    def __init__(
        self,
        dataclass: dataclasses.dataclass,
        prefilled_selectors: dict[str, Selector],
        selected_fields: list[SelectedField] = None,
    ):
        self._dataclass = dataclass
        self._prefilled_selectors = prefilled_selectors
        self._selected_fields = selected_fields

        if selected_fields is None:
            self._selected_lookup = {}
            self._selection_names = {
                field.name for field in dataclasses.fields(self._dataclass)
            }
        else:
            self._selected_lookup = {
                f.name: f for f in selected_fields
            }
            self._selection_names = {
                f.name for f in selected_fields
            }

    def __repr__(self):
        return f"DataclassSelector({self._dataclass}, {self._selection_names})"

    def __restrict__(self, selected_fields: SelectedFields) -> Self:
        return DataclassSelector(
            dataclass=self._dataclass,
            prefilled_selectors=self._prefilled_selectors,
            selected_fields=selected_fields,
        )

    def __joins__(self) -> Iterator[(str, Join, str)]:
        for name in self._selection_names:
            selector = self._prefilled_selectors[name]
            yield from joins(selector)

    def __sql__(self, builder: SQLBuilder):
        builder.write("(")
        wrote_val = False
        for name in self._selection_names:
            if wrote_val:
                builder.write(", ")
            wrote_val = True
            selector = self._prefilled_selectors[name]
            selector.__sql__(builder)
        builder.write(")")

    def __extractor__(
        self, builder: SQLBuilder, alias: str = None
    ) -> Extractor:
        field_aliases = {}
        for name in self._selection_names:
            selector = self._prefilled_selectors[name]
            if not isinstance(selector, Selector):
                selector = PythonOnlyValue(selector)
            extractor = selector.__extractor__(builder)
            field_aliases[name] = (selector, extractor)
        return ModelExtractor(self._dataclass, field_aliases, None, None)

    def __getattribute__(self, item):
        if item.startswith("_"):
            return object.__getattribute__(self, item)
        else:
            return self._prefilled_selectors[item]



class ListSelector(Selector[V]):
    def __init__(self, inner_selector: Selector[V]):
        self.inner_selector = inner_selector

    def __model_reference__(self) -> Optional[ModelReference]:
        return self.inner_selector.__model_reference__()

    def __inner_selector__(self) -> Selector:
        return self.inner_selector.__inner_selector__()

    def __joins__(self) -> Iterator[(str, str)]:
        yield from self.inner_selector.__joins__()

    def __sql__(self, builder: SQLBuilder):
        self.inner_selector.__sql__(builder)

    def __extractor__(self, builder: SQLBuilder, alias: str = None) -> Extractor:
        return ListExtractor(self.inner_selector.__extractor__(builder, alias), None, None)

    def select(
            self, selection_fn: Callable[[V, Info], R], info: Info | None = None
    ) -> ListSelector[R]:
        new_selector = call_with_maybe_info(
            selection_fn, self.inner_selector, info
        )
        if not isinstance(new_selector, ListSelector):
            return ListSelector(new_selector)
        return new_selector


class AscDesc:
    direction: Literal["ASC", "DESC"]

    def __init__(self, selector):
        self.selector = selector

    def __sql__(self, builder: SQLBuilder):
        self.selector.__sql__(builder)
        builder.write(f" {self.direction}")


class Asc(AscDesc):
    """
    Sort the selection Ascending.
    """

    direction = "ASC"


class Desc(AscDesc):
    """
    Sort the selection Descending.
    """

    direction = "DESC"


S = TypeVar("S", bound=Selector)
R = TypeVar("R", bound=Selector)
OrderBySelector = TypeVar(
    "OrderBySelector",
    Selector,
    tuple[Selector],
    AscDesc,
    tuple[AscDesc, ...],
)
WhereSelector = TypeVar("WhereSelector", bound=Selector[bool])
NewWhereSelector = TypeVar("NewWhereSelector", bound=Selector[bool])
PkValue = int | uuid.UUID | str


class ObjectSet(Generic[T, S]):
    def __init__(self, model: Type[T], conn: AsyncConnection, info: Info = None, fields: SelectedFields = None, one=False):
        self.model = model
        self.list_select = False
        self.conn = conn
        self.model_reference = ModelReference.new(model, self)
        self.model_selector = ModelSelector(self.model_reference, selected_fields=fields)
        self.pk_selector = pk_selection(self.model_selector)

        self.selection = self.model_selector
        self.where_clause: WhereSelector | None = None
        self.joins: dict[str, Join] = {}
        self.join_fields: defaultdict[str, set[str]] = defaultdict(set)
        self.seen_join_fields: set[(str, str)] = set()
        self.lock = asyncio.Lock()
        self.row_cache = None
        self.cache = None
        self.cache_main_extractor = None
        self.cache_pk_extractor = None
        self.order_by_clause: OrderBySelector | None = None
        self.where_clause: Selector[bool] | None = None
        self.group_by_clause: Selector[V] | None = None
        self.offset_clause: Selector[int] | None = None
        self.limit_clause: Selector[int] | None = Value(1) if one else None
        self.info: Info | None = info
        self._one = one
        self.post_init(info)

    def post_init(self, info: Info):
        selector = self.model_selector
        if hasattr(self.model, "__where__"):
            self.where_clause = call_with_maybe_info(
                self.model.__where__, selector, info
            )
            self.sync_joins(self.where_clause)

        if hasattr(self.model, "__group_by__"):
            self.group_by_clause = call_with_maybe_info(
                self.model.__group_by__, selector, info
            )

            self.sync_joins(self.group_by_clause)

        if hasattr(self.model, "__order_by__"):
            self.order_by_clause = call_with_maybe_info(
                self.model.__order_by__, selector, info
            )
            self.sync_joins(self.order_by_clause)

    def sync_joins(self, clause):
        for join_id, join, join_field in joins(clause, seen=self.seen_join_fields):
            self.joins.setdefault(join_id, join)
            self.join_fields[join_id].add(join_field)

    def clone(self) -> Self:
        new_self = copy.copy(self)
        new_self.row_cache = None
        new_self.cache = None
        new_self.cache_main_extractor = None
        new_self.cache_pk_extractor = None
        new_self.joins = copy.copy(self.joins)
        new_self.join_fields = copy.copy(self.join_fields)
        new_self.seen_join_fields = copy.copy(self.seen_join_fields)
        return new_self

    def select(
        self, selection: Callable[[S], R]
    ) -> ObjectSet[T, R]:
        new_self = self.clone()
        new_self.selection = selection(new_self.selection)

        new_self.sync_joins(new_self.selection)
        return new_self

    def from_cache_extractors(self, model_reference, field):
        if pk_extractor := self.cache_main_extractor.for_field(model_reference, field):
            return pk_extractor
        elif pk_extractor := self.cache_pk_extractor.for_field(model_reference, field):
            return pk_extractor

    async def sync_cache(self, new_self):
        print("syncing....", isinstance(new_self.selection, WrappedSelector))

        if (
            self.row_cache is not None
            and self.cache is not None
            and (
                isinstance(new_self.selection, WrappedSelector)
            )
        ):

            # model_pk = pk_columns(new_self.model_reference.model)
            selection = new_self.selection

            # model_ref = new_self.model_reference

            field = selection.__field__()
            if not field:
                print("Has no field", selection)
                return

            parent_selector = self.selection.__inner_selector__()
            print("Attempting to sync", selection, parent_selector)

            if isinstance(parent_selector, ModelSelector):
                # The parent was a model, so this value's should be keyed off that selector instead of it's parent
                model_ref = parent_selector.__model_reference__()
                model_pk = pk_columns(model_ref.model)
                # If we can't make an extractor from the parent extractors, bail on cache sync...
                if isinstance(model_pk, tuple):
                    pk_extractors = []

                    for pk in model_pk:
                        if pk_extractor := self.from_cache_extractors(model_ref, pk):
                            pk_extractors.append(pk_extractor)
                        else:
                            print(f"not found {model_ref.model} {pk}")
                            return
                    pk_extractor = TupleExtractor(pk_extractors, None, None)
                else:
                    if pk_extractor := self.from_cache_extractors(model_ref, model_pk):
                        pk_extractor = pk_extractor
                    else:
                        # print("\n\n--")
                        # print(self.cache_main_extractor, self.cache_pk_extractor)
                        # print(self.cache_main_extractor.extractor.extractor.field_aliases.keys())
                        print(f"not found pk {model_ref.model} {model_pk}")
                        return
            else:
                model_ref = self.model_reference
                pk_extractor = self.cache_pk_extractor

            print(f"\nTrying to sync new selection {selection}.")
            print(f"Model Ref {model_ref} with pk {pk_extractor}.")
            print(f"\n")
            inner_selection = selection.__inner_selector__()
            print(f"inner_selection: {inner_selection}")
            sub_extractor = self.cache_main_extractor.unwrap().sub_extractor(field.name)
            if sub_extractor is None:
                print(f"not found sub_extractor {model_ref.model} {field.name}")
                return

            print(f"all columns found... syncing {sub_extractor}")

            new_self.cache_main_extractor = sub_extractor
            new_self.cache_pk_extractor = pk_extractor
            new_self.row_cache = self.row_cache.copy()
            new_self.cache = sub_extractor.reset_cache()
            new_self.model_reference = model_ref

            for _pk, row in new_self.row_cache:
                pk = await pk_extractor.extract(row)
                value = await sub_extractor.extract(row)
                sub_extractor.add_to_cache(new_self.cache, pk, value)

    def where(
        self, where: Callable[[S], NewWhereSelector]
    ) -> ObjectSet[T, S]:
        new_self = self.clone()
        new_self.where_clause = where(
            new_self.selection
        )
        new_self.sync_joins(new_self.where_clause)

        return new_self

    def order_by(self, order_by: Callable[[S], OrderBySelector]) -> Self:
        new_self = self.clone()
        new_self.order_by_clause = order_by(new_self.selection)
        new_self.sync_joins(new_self.order_by_clause)

        return new_self

    def limit(self, limit: Callable[[S], Selector[int] | int] | int) -> Self:
        new_self = self.clone()
        if callable(limit):
            new_self.limit_clause = limit(
                new_self.selection
            )
            new_self.sync_joins(new_self.limit_clause)
        else:
            new_self.limit_clause = limit

        return new_self

    def offset(self, offset: Callable[[S], Selector[int] | int] | int) -> Self:
        new_self = self.clone()
        if callable(offset):
            new_self.offset_clause = offset(new_self.selection)
            new_self.sync_joins(new_self.offset_clause)
        else:
            new_self.offset_clause = offset

        return new_self

    def join(
        self,
        other_model: Type[J],
        on: Callable[[Selector[T], Selector[J]], Selector[bool] | bool],
        info: Info,
        as_list: bool = False,
        reference_id: str | None = None,
        join_type: JOIN_TYPES = "INNER",
    ) -> Self:
        new_self = self.clone()
        join_reference = ModelReference.new(
            other_model, new_self, reference_id=reference_id
        )
        join_name = f"joins_{join_reference.id}"

        object_set = None
        if (
            hasattr(other_model, "__where__")
            or hasattr(other_model, "__group_by__")
            or hasattr(other_model, "__order_by__")
        ):
            object_set = ObjectSet(model=other_model, conn=new_self.conn, info=info)
            if group_by := object_set.group_by_clause:
                object_set.pk_selector = group_by
            else:
                object_set.pk_selector = None
            # object_set.selection = WildCardSelector(object_set.model_reference)

        if join_name in new_self.joins:
            join_selection = ModelSelector(join_reference, join=new_self.joins[join_name])
        else:
            join = Join(
                id=join_name,
                model_reference=join_reference,
                on=Value(False),  # Lazily build the onclause later...
                object_set=object_set,
                join_type=join_type,
            )

            join_selection = ModelSelector(join_reference, join=join)

            if isinstance(new_self.selection, ListSelector):
                real_selector = new_self.selection.inner_selector
            else:
                real_selector = new_self.selection

            on_clause = on(real_selector, join_selection)

            join.on = on_clause
            new_self.joins[join_name] = join
            new_self.sync_joins(on_clause)

        if as_list:
            new_self.selection = ListSelector(join_selection)
        else:
            new_self.selection = join_selection
        # self.sync_cache(new_self)
        return new_self

    def __sql__(self, builder: SQLBuilder, join_fields: set[str] = None):
        return self.build_select_statement(builder, join_fields)

    def build_select_statement(self, builder: SQLBuilder, join_fields: set[str] = None):
        builder.write("SELECT ")
        builder.wrote_alias = False
        if pk_selections := self.pk_selector:
            if isinstance(pk_selections, tuple):
                pk_extractors = []
                for selection in pk_selections:  # type: ColumnSelector
                    pk_extractors.append(
                        selection.__extractor__(builder)
                    )
                pk_extractors = TupleExtractor(pk_extractors, None, None)
            else:
                pk_extractors = pk_selections.__extractor__(
                    builder
                )
        else:
            pk_extractors = None

        if join_fields is None:
            main_extractor = self.selection.__extractor__(builder)
        else:
            main_extractor = TupleExtractor(
                [
                    selection.__extractor__(builder)
                    for selection in (getattr(self.selection, jf) for jf in join_fields)
                ],
                None,
                None
            )

        builder.write(" FROM ")

        self.model_reference.__sql__(builder)
        builder.write(" AS ")
        builder.write(self.model_reference.alias())

        for join_id, join in self.joins.items():
            builder.write(" LEFT JOIN ")
            join.__sql__(builder, self.join_fields[join_id])
            builder.write(" AS ")
            builder.write(join.model_reference.alias())
            builder.write(" ON ")
            join.on.__sql__(builder)

        if self.where_clause is not None:
            builder.write(" WHERE ")
            self.where_clause.__sql__(builder)

        if self.group_by_clause is not None:
            builder.write(" GROUP BY ")
            write_single_or_tuple(self.group_by_clause, builder)

        if self.order_by_clause is not None:
            builder.write(" ORDER BY ")
            write_single_or_tuple(self.order_by_clause, builder)

        if self.offset_clause is not None:
            builder.write(" OFFSET ")
            write_single_or_tuple(self.offset_clause, builder)

        if self.limit_clause is not None:
            builder.write(" LIMIT ")
            write_single_or_tuple(self.limit_clause, builder)

        return pk_extractors, main_extractor

    async def as_list(self) -> list[V]:
        await self.load_cache()
        return list(self.cache.values())

    async def resolve(self) -> list[V] | V:
        if self._one:
            return await self.one()
        else:
            return await self.as_list()

    def __aiter__(self):
        async def f():
            l = await self.as_list()
            for elem in l:
                yield elem
        return aiter(f())

    async def one(self) -> Optional[V]:
        async for item in self:
            return item

    async def for_pk(self, pk: PkValue | tuple[PkValue, ...]) -> Optional[V]:
        await self.load_cache()
        return self.cache.get(pk)

    async def load_cache(self):
        async with self.lock:
            if self.row_cache is None:
                await self.load_data()

    async def load_data(self):
        builder = SQLBuilder()
        pk_extractor, main_extractor = self.build_select_statement(builder)
        print("*****     ", builder.q)
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(builder.q, builder.vars)
            self.row_cache = []
            self.cache = main_extractor.reset_cache()
            self.cache_main_extractor = main_extractor
            self.cache_pk_extractor = pk_extractor
            async for row in cur:
                pk = await pk_extractor.extract(row)

                self.row_cache.append((pk, row))
                value = await main_extractor.extract(row)
                main_extractor.add_to_cache(self.cache, pk, value)


class InsertSet(Generic[T, V]):
    def __init__(
        self,
        model_reference: ModelReference[T],
        conn: AsyncConnection,
        columns: list[ColumnField],
        values: list[tuple[V, ...]],
        one=False,
        returning: Selector[V] | None = None,
    ):
        if not values:
            raise RhubarbException(f"Nothing to insert.")

        self.model = model_reference.model
        self.model_reference = model_reference
        self.conn = conn
        self.columns = columns
        self.values = values
        self.returning = returning
        self._one = one

    @overload
    async def execute(self) -> list[V]:
        ...

    @overload
    async def execute(self, one: bool = True) -> V:
        ...

    async def execute(self, one=False):
        builder = SQLBuilder()
        returning_extractor = self.build_insert_statement(builder)
        print("*****     ", builder.q, builder.vars)
        if returning_extractor is not None:
            async with self.conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(builder.q, builder.vars)
                return_rows = []
                async for row in cur:
                    value = await returning_extractor.extract(row)
                    if one:
                        return value
                    return_rows.append(value)
                return return_rows
        else:
            await self.conn.execute(builder.q, builder.vars)

    def start_sql_statement(self, builder: SQLBuilder):
        builder.write("INSERT INTO ")
        self.model_reference.__sql__(builder)
        builder.write(" AS ")
        builder.write(self.model_reference.alias())
        wrote_val = False
        builder.write(" (")
        for column_field in self.columns:
            if not column_field.virtual:
                if wrote_val:
                    builder.write(", ")
                wrote_val = True
                builder.write(column_field.column_name)
        builder.write(") VALUES ")
        wrote_row = False
        for row in self.values:
            if wrote_row:
                builder.write(", ")
            wrote_row = True
            builder.write("(")
            wrote_v = False
            for v in row:
                if wrote_v:
                    builder.write(", ")
                wrote_v = True
                builder.write_value(v)
            builder.write(")")

    def build_insert_statement(self, builder: SQLBuilder):
        self.start_sql_statement(builder)

        if self.returning is not None:
            builder.write(" RETURNING ")
            return self.returning.__extractor__(builder)

    async def as_object_set(self, info):
        self.returning = ModelSelector(self.model_reference, selected_fields=[SelectedField(name=n, arguments={}, directives={}, selections=[]) for n in pk_column_names(self.model)])
        objects = await self.execute()
        pks = [pk_concrete(obj) for obj in objects]
        return ObjectSet(self.model, self.conn, info, one=self._one).where(lambda obj: func("IN", pk_selection(obj), func("", *pks), infixed=True))


class ModelUpdater(Generic[T]):
    def __init__(self, selector: ModelSelector):
        self._selector = selector
        self._setters = {}

    def __getattribute__(self, item):
        if item.startswith("_"):
            return object.__getattribute__(self, item)
        return getattr(self._selector, item)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return object.__setattr__(self, key, value)
        underlying_field = getattr(self._selector, key)
        if isinstance(underlying_field, ColumnSelector):
            self._setters[underlying_field._field.column_name] = value
        else:
            raise RhubarbException(
                f"Cannot set {key} because it is not a non-virtual Column Field."
            )


class UpdateSet(Generic[T, V]):
    def __init__(
        self,
        model_reference: ModelReference[T],
        conn: AsyncConnection,
        setters: dict[str, V],
        where: Selector[bool],
        one: bool = False,
        returning: Selector[V] | None = None,
    ):
        if not setters:
            raise RhubarbException(f"Nothing to update.")

        self.where_clause = where
        self.model = model_reference.model
        self.model_reference = model_reference
        self.conn = conn
        self.setters = setters
        self.where = where
        self._one = one
        self.returning = returning
        self.joins: dict[str, Join] = {}
        self.join_fields: defaultdict[str, set[str]] = defaultdict(set)
        self.seen_join_fields: set[(str, str)] = set()

        self.sync_joins(self.where)
        for value in self.setters.values():
            self.sync_joins(value)
        if returning is not None:
            self.sync_joins(self.returning)

    async def as_object_set(self, info):
        self.returning = ModelSelector(self.model_reference, selected_fields=[SelectedField(name=n, arguments={}, directives={}, selections=[]) for n in pk_column_names(self.model)])
        objects = await self.execute()
        pks = [pk_concrete(obj) for obj in objects]
        return ObjectSet(self.model, self.conn, info, one=self._one).where(lambda obj: func("IN", pk_selection(obj), func("", *pks), infixed=True))

    def sync_joins(self, clause):
        for join_id, join, join_field in joins(clause, seen=self.seen_join_fields):
            self.joins.setdefault(join_id, join)
            self.join_fields[join_id].add(join_field)

    @overload
    async def execute(self) -> list[V]:
        ...

    @overload
    async def execute(self, one: bool = True) -> V:
        ...

    async def execute(self, one=None):
        builder = SQLBuilder()
        returning_extractor = self.build_update_statement(builder)
        print("*****     ", builder.q)
        if returning_extractor is not None:
            async with self.conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(builder.q, builder.vars)
                return_rows = []
                async for row in cur:
                    value = await returning_extractor.extract(row)
                    if one:
                        return value
                    return_rows.append(value)
                return return_rows
        else:
            await self.conn.execute(builder.q, builder.vars)

    def start_sql_statement(self, builder: SQLBuilder):
        builder.write("UPDATE ")
        self.model_reference.__sql__(builder)
        builder.write(" AS ")
        builder.write(self.model_reference.alias())
        builder.write(" SET ")
        wrote_val = False
        for k, v in self.setters.items():
            if wrote_val:
                builder.write(", ")
            wrote_val = True
            builder.write(f"{k} = ")
            builder.write_value(v)

    def build_update_statement(self, builder: SQLBuilder):
        self.start_sql_statement(builder)

        wrote_join = False
        where_clause = self.where_clause
        for join_id, join in self.joins.items():
            if not wrote_join:
                wrote_join = True
                builder.write(" FROM ")
                join.__sql__(builder, self.join_fields[join_id])
                builder.write(" AS ")
                builder.write(join.model_reference.alias())
                if where_clause is not None:
                    where_clause &= join.on
                else:
                    where_clause = join.on
            else:
                builder.write(" LEFT JOIN ")
                join.__sql__(builder, self.join_fields[join_id])
                builder.write(" AS ")
                builder.write(join.model_reference.alias())
                builder.write(" ON ")
                join.on.__sql__(builder)

        if where_clause is not None:
            builder.write(" WHERE ")
            where_clause.__sql__(builder)

        if self.returning is not None:
            builder.write(" RETURNING ")
            return self.returning.__extractor__(builder)


class DeleteSet(Generic[T, V]):
    def __init__(
        self,
        model_reference: ModelReference[T],
        conn: AsyncConnection,
        where: Selector[bool],
        returning: Selector[V] | None = None,
    ):
        self.where_clause = where
        self.model = model_reference.model
        self.model_reference = model_reference
        self.conn = conn
        self.where = where
        self.returning = returning
        self.joins: dict[str, Join] = {}
        self.join_fields: defaultdict[str, set[str]] = defaultdict(set)
        self.seen_join_fields: set[(str, str)] = set()

        self.sync_joins(self.where)
        if returning is not None:
            self.sync_joins(self.returning)

    def sync_joins(self, clause):
        for join_id, join, join_field in joins(clause, seen=self.seen_join_fields):
            self.joins.setdefault(join_id, join)
            self.join_fields[join_id].add(join_field)

    @overload
    async def execute(self) -> list[V]:
        ...

    @overload
    async def execute(self, one: bool = True) -> V:
        ...

    async def execute(self, one=None):
        builder = SQLBuilder()
        returning_extractor = self.build_delete_statement(builder)
        print("*****     ", builder.q)
        if returning_extractor is not None:
            async with self.conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(builder.q, builder.vars)
                return_rows = []
                async for row in cur:
                    value = await returning_extractor.extract(row)
                    if one:
                        return value
                    return_rows.append(value)
                return return_rows
        else:
            await self.conn.execute(builder.q, builder.vars)

    def start_sql_statement(self, builder: SQLBuilder):
        builder.write("DELETE FROM ")
        self.model_reference.__sql__(builder)
        builder.write(" AS ")
        builder.write(self.model_reference.alias())

    def build_delete_statement(self, builder: SQLBuilder):
        self.start_sql_statement(builder)

        wrote_join = False
        where_clause = self.where_clause
        for join_id, join in self.joins.items():
            if not wrote_join:
                wrote_join = True
                builder.write(" FROM ")
                join.__sql__(builder, self.join_fields[join_id])
                builder.write(" AS ")
                builder.write(join.model_reference.alias())
                if where_clause is not None:
                    where_clause &= join.on
                else:
                    where_clause = join.on
            else:
                builder.write(" LEFT JOIN ")
                join.__sql__(builder, self.join_fields[join_id])
                builder.write(" AS ")
                builder.write(join.model_reference.alias())
                builder.write(" ON ")
                join.on.__sql__(builder)

        if where_clause is not None:
            builder.write(" WHERE ")
            where_clause.__sql__(builder)

        if self.returning is not None:
            builder.write(" RETURNING ")
            return self.returning.__extractor__(builder)


def pk_concrete(
    obj: T,
) -> ColumnSelector[V] | tuple[ColumnSelector[V], ...]:
    if cached_pk := getattr(obj, "_cached_pk", None):
        return cached_pk
    model_pk = getattr(obj, "__pk__")
    if isinstance(model_pk, str):
        return getattr(obj, model_pk)
    return tuple([getattr(obj, pk) for pk in model_pk])


def pk_column_names(
    model: T,
) -> set[str]:
    if isinstance(model.__pk__, str):
        return {model.__pk__}
    return set(model.__pk__)


def pk_selection(
    model: ModelSelector[T],
) -> ColumnSelector[V] | tuple[ColumnSelector[V], ...]:
    model_pk = model._model_reference.model.__pk__
    if isinstance(model_pk, str):
        return getattr(model, model_pk)
    return tuple([getattr(model, pk) for pk in model_pk])


def is_rhubarb_field(field: StrawberryField):
    return isinstance(field, RelationField) or isinstance(field, ColumnField)


def columns(
    model: Type[T], virtual=None, insert_default=None, update_default=None, inlinable=None
) -> Iterator[ColumnField]:
    for field in dataclasses.fields(model):
        if isinstance(field, ColumnField):
            if virtual is not None and field.virtual != virtual:
                continue
            if insert_default is not None and field.insert_default != insert_default:
                continue
            if update_default is not None and field.update_default != update_default:
                continue
        elif isinstance(field, RelationField):
            if inlinable and not field.force_inline and isinstance(field.type, (StrawberryList, list)):
                continue
            if virtual is not None and not virtual:
                continue
            if insert_default is not None and insert_default:
                continue
            if update_default is not None and update_default:
                continue
        else:
            if virtual is not None and not virtual:
                continue
            if insert_default is not None and insert_default:
                continue
            if update_default is not None and update_default:
                continue
        yield field

def get_column(model: Type[T], field_name: str) -> ColumnField:
    if field := model._type_definition.get_field(field_name):
        if isinstance(field, ColumnField):
            return field
    raise RhubarbException(f"Could not find field {field_name} on model {model}")


def pk_columns(model: Type[T]) -> tuple[ColumnField, ...] | ColumnField:
    if isinstance(model.__pk__, tuple):
        return tuple(get_column(model, pk) for pk in model.__pk__)
    return get_column(model, model.__pk__)


def joins(selector: Selector[T], seen=None) -> Iterator[(str, Join, str)]:
    seen = seen or set()
    if not hasattr(selector, "__joins__"):
        return
    for join_id, join, field_name in selector.__joins__():
        if (join_id, field_name) not in seen:
            seen.add((join_id, field_name))
            yield join_id, join, field_name


class ColumnField(StrawberryField):
    def __init__(
        self,
        *args,
        virtual: False,
        references: str | None = None,
        column_name: str | None = None,
        column_type: SqlType | None = None,
        insert_default: DEFAULT_SQL_FUNCTION = dataclasses.MISSING,
        update_default: DEFAULT_SQL_FUNCTION = dataclasses.MISSING,
        sql_default: DEFAULT_SQL_FUNCTION = dataclasses.MISSING,
        **kwargs,
    ):
        self.virtual = virtual
        self.references = references
        self.insert_default = insert_default
        self.update_default = update_default
        self._column_name = column_name
        self._column_type = column_type
        self.sql_default = sql_default
        super().__init__(*args, **kwargs)

    @property
    def column_name(self) -> str:
        return self._column_name or self.name

    @property
    def column_type(self) -> SqlType:
        return self._column_type or SqlType.from_python(self.type)

    def __repr__(self):
        return f"ColumnField({self.column_name}, {self.column_type})"


def column(
    fn: Optional[Callable] = None,
    *,
    virtual: bool = False,
    references: Optional[str] = None,
    python_name: Optional[str] = None,
    graphql_name: Optional[str] = None,
    column_name: Optional[str] = None,
    description: Optional[str] = None,
    permission_classes: List[Type[BasePermission]] = (),  # type: ignore
    default: DEFAULT_SQL_FUNCTION = dataclasses.MISSING,
    insert_default: DEFAULT_SQL_FUNCTION = dataclasses.MISSING,
    update_default: DEFAULT_SQL_FUNCTION = dataclasses.MISSING,
    sql_default: DEFAULT_SQL_FUNCTION = dataclasses.MISSING,
    default_factory: Union[Callable[[], Any], object] = dataclasses.MISSING,
    metadata: Optional[Mapping[Any, Any]] = None,
    deprecation_reason: Optional[str] = None,
    directives: Sequence[object] = (),
    graphql_type: Optional[Any] = None,
    extensions: List[FieldExtension] = (),  # type: ignore
):
    if (
        insert_default != dataclasses.MISSING or update_default != dataclasses.MISSING
    ) and default_factory == dataclasses.MISSING:
        default_factory = default_function_to_python(
            insert_default if update_default == dataclasses.MISSING else update_default
        )
    elif not virtual and default == dataclasses.MISSING:
        default = UNSET

    type_annotation = StrawberryAnnotation.from_annotation(graphql_type)

    field = ColumnField(
        virtual=virtual,
        references=references,
        type_annotation=type_annotation,
        python_name=python_name,
        graphql_name=graphql_name,
        column_name=column_name,
        description=description,
        permission_classes=permission_classes,
        default=default,
        default_factory=default_factory,
        insert_default=insert_default,
        update_default=update_default,
        sql_default=sql_default,
        metadata=metadata,
        deprecation_reason=deprecation_reason,
        directives=directives,
        extensions=extensions,
    )

    if fn:
        return field(fn)
    return field


virtual_column = functools.partial(column, virtual=True)


@dataclasses.dataclass(kw_only=True)
class Registry:
    id: int = dataclasses.field(default_factory=new_ref_id)
    entries: set[SupportsSqlModel] = dataclasses.field(default_factory=set)
    other_registries: dict[int, Self] = dataclasses.field(default_factory=dict)

    def add_entry(self, cls: Type[T]):
        self.entries.add(cls)

    def values(self, seen: set):
        for cls in self.entries:
            if cls not in seen:
                seen.add(cls)
                yield cls
            for registry in self.other_registries.values():
                yield from registry.values(seen)

    def other_registry(self, registry: Registry):
        self.other_registries[registry.id] = registry


DEFAULT_REGISTRY = Registry()

@overload
def table(
    registry: Registry = DEFAULT_REGISTRY,
    name: Optional[str] = None,
    description: Optional[str] = None,
    directives: Optional[Sequence[object]] = (),
    extend: bool = False,
) -> Callable[[Type[T]], Type[T]]:
    ...


@overload
def table(
    cls: Type,
    *,
    registry: Registry = DEFAULT_REGISTRY,
    name: Optional[str] = None,
    description: Optional[str] = None,
    directives: Optional[Sequence[object]] = (),
    extend: bool = False,
) -> Type[T]:
    ...


def table(
    cls: Optional[Type] = None,
    *,
    registry: Optional[Registry] = DEFAULT_REGISTRY,
    name: Optional[str] = None,
    description: Optional[str] = None,
    directives: Optional[Sequence[object]] = (),
    extend: bool = False,
):
    if cls:
        new_type = strawberry.type(
            cls, name=name, description=description, directives=directives, extend=extend
        )
        if registry is not None:
            registry.add_entry(new_type)
        return new_type
    else:
        new_type = strawberry.type(
            name=name, description=description, directives=directives, extend=extend
        )
        def wrapper(real_cls):
            if registry is not None:
                registry.add_entry(real_cls)
            return new_type(real_cls)
        return wrapper


class RelationField(StrawberryField[J]):
    virtual = True

    def __init__(self, other_table_annotation, force_inline: bool = False, **kwargs):
        self.other = other_table_annotation
        self.force_inline = force_inline
        super().__init__(**kwargs)


class RelationAnnotation(StrawberryAnnotation):
    def __init__(self, lazy_resolver: Type[J] | Callable[[], J]):
        self.lazy_resolver = lazy_resolver
        super().__init__(None)

    def resolve(self) -> Union[StrawberryType, type]:
        if self.annotation is None:
            if inspect.isfunction(self.lazy_resolver):
                self.annotation = Callable[[], self.lazy_resolver()]
            else:
                self.annotation = self.lazy_resolver
        return super().resolve()


ReferenceFn = Optional[Callable[[ModelReference[T], ModelReference[J], Info], bool]]


def get_relation_annotation(annotations):
    annotations.pop("self", None)
    for k, v in list(annotations.items()):
        if isinstance(v, Info) or v == "Info":
            annotations.pop(k, None)
    return next(x for x in annotations.values())


def relation(
    base_resolver: ReferenceFn | None = None,
    force_inline: bool = False,
    python_name: Optional[str] = None,
    graphql_name: Optional[str] = None,
    description: Optional[str] = None,
    permission_classes: List[Type[BasePermission]] = (),  # type: ignore
    default: object = dataclasses.MISSING,
    default_factory: Union[Callable[[], Any], object] = dataclasses.MISSING,
    metadata: Optional[Mapping[Any, Any]] = None,
    deprecation_reason: Optional[str] = None,
    directives: Sequence[object] = (),
    extensions: List[FieldExtension] = (),  # type: ignore
    graphql_type: Optional[Any] = None,
    join_type: JOIN_TYPES = "INNER",
) -> Callable[[], J] | Callable[[ReferenceFn], Callable[[], J]]:
    def wrap(passed_resolver) -> Callable[[], J]:
        reference_id = new_ref_id()

        def real_resolver(root: ModelSelector, info: Info):
            model_ref_id = root._model_reference.id
            full_reference_id = f"{model_ref_id}_{reference_id}"
            resolved_annotations = inspect.get_annotations(
                passed_resolver, eval_str=True
            )
            other_table = get_relation_annotation(resolved_annotations)
            as_list = graphql_type is not None and hasattr(graphql_type, "__origin__") and issubclass(getattr(graphql_type, "__origin__"), list)
            return root._model_reference.object_set.join(
                other_table,
                on=passed_resolver,
                reference_id=full_reference_id,
                info=info,
                join_type=join_type,
                as_list=as_list
            ).selection

        try:
            annotations = inspect.get_annotations(passed_resolver)
            other_table_annotation = get_relation_annotation(annotations)
        except StopIteration:
            raise RhubarbException(
                f"Resolver passed to relation {passed_resolver} does not have an annotation to use for related Model"
            )

        if graphql_type is not None:
            type_annotation = StrawberryAnnotation.from_annotation(graphql_type)
        else:
            type_annotation = StrawberryAnnotation.from_annotation(other_table_annotation)
        return RelationField(
            other_table_annotation=other_table_annotation,
            force_inline=force_inline,
            base_resolver=StrawberryResolver(real_resolver),
            python_name=python_name,
            graphql_name=graphql_name,
            type_annotation=type_annotation,
            description=description,
            permission_classes=permission_classes,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            deprecation_reason=deprecation_reason,
            directives=directives,
            extensions=extensions,
        )

    if base_resolver is not None:
        return wrap(base_resolver)
    return wrap


def optimize_selection(selected_fields: SelectedFields, selection):
    if isinstance(selection, ModelSelector):
        selection = selection.__restrict__(selected_fields)
    elif isinstance(selection, WrappedSelector):
        selection._selector = optimize_selection(selected_fields, selection._selector)
    elif isinstance(selection, ListSelector):
        selection.inner_selector = optimize_selection(selected_fields, selection.inner_selector)
    elif dataclasses.is_dataclass(selection):
        selection = DataclassSelector(selection.__class__, {
            f.name: getattr(selection, f.name) for f in dataclasses.fields(selection)
        }, selected_fields)
    return selection


def sum_agg(model_selector: ModelSelector, column: Selector):
    return Aggregate(model_selector, args=[column], op="SUM", infixed=False)


def count_agg(model_selector: ModelSelector, column: Selector):
    return Aggregate(model_selector, args=[column], op="COUNT", infixed=False)


def avg_agg(model_selector: ModelSelector, column: Selector):
    return Aggregate(model_selector, args=[column], op="AVG", infixed=False)


def max_agg(model_selector: ModelSelector, column: Selector):
    return Aggregate(model_selector, args=[column], op="MAX", infixed=False)


def min_agg(model_selector: ModelSelector, column: Selector):
    return Aggregate(model_selector, args=[column], op="MIN", infixed=False)


def string_agg(
    model_selector: ModelSelector, column: Selector, delimeter: Selector[str]
):
    return Aggregate(
        model_selector, args=[column, delimeter], op="STRING_AGG", infixed=False
    )


def array_agg(model_selector: ModelSelector, column: Selector):
    return Aggregate(model_selector, args=[column], op="ARRAY_AGG", infixed=False)


def json_agg(model_selector: ModelSelector, column: Selector):
    return Aggregate(model_selector, args=[column], op="JSON_AGG", infixed=False)


def concat(*args: Selector[str] | str):
    return Computed(args=list(args), op="CONCAT", infixed=False)


def val(v: Any):
    return Value(v)


def func(fn: str, *args: Selector, infixed=False):
    return Computed(list(args), op=fn, infixed=infixed)


def agg(ms: ModelSelector, fn: str, *args: Selector, infixed=False):
    return Aggregate(ms, args=list(args), op=fn, infixed=infixed)


def use(fn: Callable[..., V], *depends_on: Selector, **kw_depends_on: Selector) -> UseSelector[V]:
    return UseSelector(fn, list(depends_on), kw_depends_on)


def python_field(depends_on: Callable[[ModelSelector], list[Selector] | Selector | dict[str, Selector]]) -> Callable[[Callable[..., V]], ColumnField]:
    def wrap(fn):
        wrapped_field = strawberry.field(fn)
        sig = inspect.signature(fn)

        def real_fn(root: ModelSelector, info: Info):
            async def wrapped_fn(*args, **kwargs):
                result = get_result(wrapped_field, root, info, list(args), kwargs)
                if inspect.isawaitable(result):
                    result = await result
                return result
            depends = depends_on(root)
            if isinstance(depends, dict):
                args = []
                kwargs = depends
            elif isinstance(depends, tuple):
                args, kwargs = depends
            elif isinstance(depends, list):
                args = depends
                kwargs = {}
            else:
                args = [depends]
                kwargs = {}
            return UseSelector(wrapped_fn, dependencies=args, kwarg_dependencies=kwargs)
        return virtual_column(real_fn, graphql_type=sig.return_annotation)
    return wrap


def get_result(field, source, info, args, kwargs):
    if field.base_resolver.self_parameter:
        args.append(source)

    root_parameter = field.base_resolver.root_parameter
    if root_parameter:
        kwargs[root_parameter.name] = source

    info_parameter = field.base_resolver.info_parameter
    if info_parameter:
        kwargs[info_parameter.name] = info

    return field.get_result(source, info, args, kwargs)


field = strawberry.field