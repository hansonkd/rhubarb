import copy
from typing import Type, Callable, Optional

import psycopg.errors
from psycopg import AsyncConnection, Rollback
from strawberry.types import Info

from rhubarb.core import (
    default_function_to_python,
    T,
    V,
    call_with_maybe_info,
    Unset,
    SQLValue,
)
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
    pk_selection,
)


def query(
    conn: AsyncConnection, m: Type[T], info: Info = None, one=False
) -> ObjectSet[T, ModelSelector[T]]:
    return ObjectSet(m, conn=conn, info=info, one=one)


def reload(
    conn: AsyncConnection, m: T, info: Info = None
) -> ObjectSet[T, ModelSelector[T]]:
    return by_pk(conn, m.__class__, pk_concrete(m), info)


def by_pk(
    conn: AsyncConnection,
    m: Type[T],
    pk: SQLValue | tuple[SQLValue, ...],
    info: Info = None,
) -> ObjectSet[T, ModelSelector[T]]:
    return ObjectSet(m, conn=conn, info=info, one=True).where(
        lambda x: pk_selection(x) == pk
    )


def by_kw(
    conn: AsyncConnection,
    m: Type[T],
    info: Info = None,
    **kwargs
) -> ObjectSet[T, ModelSelector[T]]:
    return ObjectSet(m, conn=conn, info=info, one=True).kw_where(
        **kwargs
    )


def delete(
    conn: AsyncConnection,
    model: Type[T],
    where: Callable[[ModelSelector], Selector[bool] | bool],
    info: Info | None = None,
    one: bool = False,
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
        one=one,
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
    conn: AsyncConnection,
    model: Type[T],
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


async def find_or_create(
    conn: AsyncConnection, obj: T, info: Info = None, **kwargs
) -> T:
    model = obj.__class__
    if obj := await by_kw(model, info=info, **kwargs).one():
        return obj
    async with conn.transaction() as txn:
        try:
            return await save(obj, conn, info=info).execute()
        except psycopg.errors.UniqueViolation:
            raise Rollback(txn)
    return await by_kw(model, info=info, **kwargs).one()


def empty_pk(obj: T):
    pk = pk_concrete(obj)
    return (
        pk is None
        or isinstance(pk, Unset)
        or isinstance(obj, tuple)
        and all(p is None or isinstance(p, Unset) for p in pk)
    )


def save(conn: AsyncConnection, obj: T, info: Info | None = None, insert_with_pk=False):
    model = obj.__class__
    if empty_pk(obj) or insert_with_pk:
        return insert_objs(
            conn, model, [obj], skip_pks=not insert_with_pk, one=True, returning=True
        )

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
    conn: AsyncConnection,
    model: Type[T],
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
    conn: AsyncConnection,
    model: Type[T],
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
