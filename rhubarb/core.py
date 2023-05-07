import base64
import datetime
import decimal
import inspect
import re
import time
import uuid
from enum import Enum
from typing import TypeVar, Protocol, ClassVar, Literal, Union, NewType

import phonenumbers
import psycopg
from psycopg import AsyncConnection
from psycopg.abc import Dumper
from strawberry import scalar
from strawberry.scalars import JSON, Base16, Base32, Base64
from strawberry.types import Info
from strawberry.types.types import TypeDefinition
from strawberry import scalars
from rhubarb.errors import RhubarbException, RhubarbValidationError

Elem = TypeVar("Elem")


DEFAULT_SQL_FUNCTION = Literal["uuid_generate_v4()", "now()", "'{}'", None, True, False]


Binary = scalar(
    NewType("Binary", bytes),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


Serial = scalar(
    NewType("Serial", int),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


def parse_phone(v):
    v = str(v)
    return phonenumbers.parse(v)


PhoneNumber = scalar(
    NewType("PhoneNumber", phonenumbers.PhoneNumber),
    serialize=lambda v: str(v),
    parse_value=parse_phone,
)


EMAIL_REGEX = re.compile(
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)


def parse_email(v):
    v = str(v)
    if not EMAIL_REGEX.fullmatch(v):
        raise RhubarbValidationError("Invalid Email {v}")
    return v


Email = scalar(
    NewType("Email", str),
    serialize=lambda v: v,
    parse_value=parse_email,
)


import bcrypt


class PasswordHashers(Enum):
    BCRYPT = "bcrypt"


class PasswordHash(object):
    def __init__(self, hash_: bytes):
        self.hash = hash_
        split = self.hash.split(b'$')
        self.algo = PasswordHashers[split[0].decode()]
        self.rounds = int(split[3].decode())

    def __eq__(self, candidate):
        if isinstance(candidate, str):
            candidate = candidate.encode()
            return bcrypt.checkpw(candidate, self.hash)
        return False

    def __repr__(self):
        return '<{}>'.format(type(self).__name__)

    def check(self, candidate: str):
        if self.algo == PasswordHashers.BCRYPT:
            return bcrypt.checkpw(candidate.encode(), self.hash)
        raise RhubarbException("Unknown algorithm")

    @classmethod
    def new(cls, password, algo=PasswordHashers.BCRYPT, rounds=None):
        if isinstance(password, str):
            password = password.encode('utf8')
        rounds = rounds or (datetime.date.today().year - 2000)
        if algo == PasswordHashers.BCRYPT:
            new_hash = bcrypt.hashpw(password, bcrypt.gensalt(rounds))
        else:
            raise RhubarbException("Unknown algorithm")
        return cls(new_hash)


Password = scalar(
    NewType("Password", bytes),
    serialize=lambda v: v.hash,
    parse_value=PasswordHash,
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
        case "'{}'":
            return lambda: []
        case other:
            if other is None or isinstance(other, bool):
                return lambda: other
            raise RhubarbException(
                f"Invalid default function to use for column {other}. Available: {DEFAULT_SQL_FUNCTION}"
            )


class SqlModel(Protocol):
    _type_definition: ClassVar[TypeDefinition]
    __schema__: str
    __table__: str
    __pk__: str | tuple[str]


ScalarSQLValue = Union[
    None,
    str,
    bytes,
    datetime.datetime,
    datetime.date,
    bool,
    int,
    float,
    dict,
    list,
    decimal.Decimal,
    SqlModel,
    JSON,
    Binary,
    Base16,
    Base32,
    Base64,
]

SQLValue = Union[ScalarSQLValue, list[ScalarSQLValue], dict[str, ScalarSQLValue]]

T = TypeVar("T", bound=SqlModel)
J = TypeVar("J", bound=SqlModel)
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
