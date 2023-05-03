import base64
import datetime
import decimal
import inspect
import time
import uuid
from typing import TypeVar, Protocol, ClassVar, Literal, Union, NewType

from psycopg import AsyncConnection
from strawberry import scalar
from strawberry.types import Info
from strawberry.types.types import TypeDefinition
from strawberry import scalars
from rhubarb.errors import RhubarbException

Elem = TypeVar("Elem")


DEFAULT_SQL_FUNCTION = Literal["uuid_generate_v4()", "now()", "null", True, False]


Binary = scalar(
    NewType("Binary", bytes),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

def new_ref_id() -> str:
    return str(time.monotonic_ns())[-5:]


def get_conn(info: Info) -> AsyncConnection:
    return info.context["conn"]


def default_function_to_python(f):
    match f:
        case "uuid_generate_v4()":
            return uuid.uuid4
        case "now()":
            return datetime.datetime.utcnow
        case other:
            if other is None or isinstance(other, bool):
                return lambda: other
            raise RhubarbException(
                f"Invalid default function to use for column {other}. Available: {DEFAULT_SQL_FUNCTION}"
            )


class SupportsSqlModel(Protocol):
    _type_definition: ClassVar[TypeDefinition]
    __schema__: str
    __table__: str
    __pk__: str | tuple[str]


SQLValue = Union[
    None,
    str,
    bytes,
    datetime.datetime,
    datetime.date,
    bool,
    int,
    float,
    decimal.Decimal,
    SupportsSqlModel,
]

T = TypeVar("T", bound=SupportsSqlModel)
J = TypeVar("J", bound=SupportsSqlModel)
V = TypeVar("V", bound=SQLValue)


class Unset:
    """Values that aren't loaded from the database"""

    def __repr__(self):
        return "rhubarb.UNSET"

    def __sql__(self, builder):
        builder.write("DEFAULT")


UNSET = Unset()


def call_with_maybe_info(f, obj, info):
    sig = inspect.signature(f)
    if len(sig.parameters) == 1:
        return f(obj)
    else:
        return f(obj, info)
