from typing import Any, Callable

from rhubarb.core import V
from rhubarb.object_set import (
    ModelSelector,
    Aggregate,
    Selector,
    SqlType,
    Computed,
    Case,
    Value,
    RawSQL,
    UseSelector,
    func,
)


func = func


def sum_agg(model_selector: ModelSelector, sel: Selector):
    return Aggregate(model_selector, args=[sel], op="SUM", infixed=False)


def count_agg(model_selector: ModelSelector, sel: Selector):
    return Aggregate(model_selector, args=[sel], op="COUNT", infixed=False)


def avg_agg(model_selector: ModelSelector, sel: Selector):
    return Aggregate(model_selector, args=[sel], op="AVG", infixed=False)


def max_agg(model_selector: ModelSelector, sel: Selector):
    return Aggregate(model_selector, args=[sel], op="MAX", infixed=False)


def min_agg(model_selector: ModelSelector, sel: Selector):
    return Aggregate(model_selector, args=[sel], op="MIN", infixed=False)


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


def coalesce(*args: Selector[str] | str):
    return Computed(args=list(args), op="COALESCE", infixed=False)


def cast(o: Selector, t: SqlType):
    return Computed(args=[o, t], op="CAST", infixed=False, sep="AS")


def is_null(o: Selector):
    return Computed(args=[o], op="IS NULL", infixed=True)


def is_not_null(o: Selector):
    return Computed(args=[o], op="IS NOT NULL", infixed=True)


def case(*whens: tuple[Selector[bool], Selector[V]], default: Selector[V] = None):
    return Case(list(whens), default=default)


def val(v: Any):
    return Value(v)


def raw(v: Any):
    return RawSQL(v)


def agg(ms: ModelSelector, fn: str, *args: Selector, infixed=False):
    return Aggregate(ms, args=list(args), op=fn, infixed=infixed)


def use(
    fn: Callable[..., V], *depends_on: Selector, **kw_depends_on: Selector
) -> UseSelector[V]:
    return UseSelector(fn, list(depends_on), kw_depends_on)
