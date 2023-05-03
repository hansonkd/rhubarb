import copy
from typing import Type, Callable

from psycopg import AsyncConnection
from strawberry.types import Info

from rhubarb.core import default_function_to_python, T, V, call_with_maybe_info, Unset
from rhubarb.object_set import (
    InsertSet,
    columns,
    ModelSelector,
    Selector,
    ObjectSet,
    pk_column_names,
    ColumnField,
    pk_concrete,
    UpdateSet,
    DeleteSet,
    ModelUpdater,
)


def query(
    m: Type[T], conn: AsyncConnection, info: Info = None
) -> ObjectSet[T, ModelSelector[T]]:
    return ObjectSet(m, conn=conn, info=info)


def delete(
    model: Type[T],
    conn: AsyncConnection,
    where: Callable[[ModelSelector], Selector[bool] | bool],
    info: Info | None = None,
    returning: Callable[[ModelSelector], Selector[bool] | bool] | None | bool = None,
):
    selected_fields = info.selected_fields
    object_set = ObjectSet(model, conn=conn, fields=selected_fields)
    model_reference = object_set.model_reference
    model_selector = object_set.model_selector
    where_selector, returning_selector = build_where_and_returning(
        model, model_selector, info, where, returning
    )
    return DeleteSet(
        model_reference,
        conn=conn,
        where=where_selector,
        returning=returning_selector,
    )


def build_where_and_returning(model, model_selector, info, where, returning):
    where_selector = where(model_selector)
    if hasattr(model, "__where__"):
        where_selector = call_with_maybe_info(model.__where__, model_selector, info)
    returning_selector = None
    if returning is not None:
        if isinstance(returning, bool) and returning:
            returning_selector = model_selector
        else:
            returning_selector = returning(model_selector)
    return where_selector, returning_selector


def build_update_set(
    info, conn, model, model_reference, setters, where_selector, returning_selector, one
):
    for default_update in columns(model, update_default=True):
        if default_update.column_name not in setters:
            setters[default_update.column_name] = default_function_to_python(
                default_update.update_default
            )()

    return UpdateSet(
        model_reference,
        conn=conn,
        setters=setters,
        where=where_selector,
        one=one,
        returning=returning_selector,
    )


def update(
    model: Type[T],
    conn: AsyncConnection,
    set_fn: Callable[[ModelUpdater], ModelUpdater | None],
    where: Callable[[ModelSelector], Selector[bool] | bool],
    info: Info | None = None,
    one=False,
    returning: Callable[[ModelSelector], Selector[bool] | bool] | None | bool = None,
):
    object_set = ObjectSet(model, conn=conn, info=info)
    model_reference = object_set.model_reference
    model_selector = object_set.model_selector
    model_updater = ModelUpdater(model_selector)
    set_fn(model_updater)
    where_selector, returning_selector = build_where_and_returning(
        model, model_selector, info, where, returning
    )

    setters = model_updater._setters
    return build_update_set(
        info,
        conn,
        model,
        model_reference,
        setters,
        where_selector,
        returning_selector,
        one,
    )


async def save(obj: T, conn: AsyncConnection, info: Info | None = None):
    model = obj.__class__
    object_set = ObjectSet(model, conn=conn, info=info)
    model_reference = object_set.model_reference
    model_selector = object_set.model_selector
    setters = {
        col_name: v
        for col_name, v in (
            (col.column_name, getattr(obj, col.name))
            for col in columns(model)
            if not col.virtual
        )
        if not isinstance(v, Unset)
    }
    pk_selectors = object_set.pk_selector
    pk_real = pk_concrete(obj)
    where_selector = Selector.__eq__(pk_selectors, pk_real)
    if hasattr(model, "__where__"):
        where_selector = call_with_maybe_info(model.__where__, model_selector, info)
    return build_update_set(
        info,
        conn,
        model,
        model_reference,
        setters,
        where_selector,
        model_selector,
        one=True,
    )


def insert(
    model: Type[T],
    conn: AsyncConnection,
    cols_fn: Callable[[ModelSelector], list[ColumnField, ...]],
    values_fn: Callable[[ModelSelector], list[tuple[V, ...]]],
    info: Info | None = None,
    returning: Callable[[ModelSelector], Selector[bool] | bool] | None | bool = None,
):
    object_set = ObjectSet(model, conn=conn, info=info)
    model_reference = object_set.model_reference
    model_selector = object_set.model_selector
    insert_columns = cols_fn(model_selector)
    values = values_fn(model_selector)
    return build_insert_set(
        info,
        conn,
        model,
        model_reference,
        model_selector,
        insert_columns,
        values,
        returning,
        one=True,
    )


def build_insert_set(
    info,
    conn,
    model,
    model_reference,
    model_selector,
    insert_columns,
    values,
    returning,
    one,
):
    returning_selector = None
    if returning is not None:
        if isinstance(returning, bool) and returning:
            returning_selector = model_selector
        else:
            returning_selector = returning(model_selector)
    for default_insert in columns(model, insert_default=True):
        if default_insert not in insert_columns:
            insert_columns.append(default_insert)
            val = default_function_to_python(default_insert.insert_default)()
            new_values = copy.copy(values)
            for xx, value in enumerate(new_values):
                values[xx] = val + (val,)
    return InsertSet(
        model_reference,
        conn=conn,
        columns=insert_columns,
        values=values,
        one=one,
        returning=returning_selector,
    )


def insert_objs(
    model: Type[T],
    conn: AsyncConnection,
    values: list[T],
    skip_pks=True,
    exclude_columns: set[str] = None,
    info: Info | None = None,
    one=False,
    returning: Callable[[ModelSelector], Selector[bool] | bool] | None | bool = None,
):
    object_set = ObjectSet(model, conn=conn, info=info)
    model_reference = object_set.model_reference
    model_selector = object_set.model_selector
    exclude = exclude_columns or set()
    if skip_pks:
        exclude |= pk_column_names(model)
    insert_columns = [
        col for col in columns(model, virtual=False) if col.name not in exclude
    ]
    insert_values = []
    for row in values:
        insert_values.append(tuple(getattr(row, f.name) for f in insert_columns))

    return build_insert_set(
        info,
        conn,
        model,
        model_reference,
        model_selector,
        insert_columns,
        insert_values,
        returning,
        one,
    )
