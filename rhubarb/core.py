import dataclasses
import datetime
import decimal
import inspect
import re
import time
import uuid
from functools import total_ordering
from typing import TypeVar, Protocol, ClassVar, Union, NewType

import phonenumbers
from psycopg import AsyncConnection
from strawberry import scalar
from strawberry.scalars import JSON, Base16, Base32, Base64
from strawberry.types import Info
from strawberry.types.types import TypeDefinition
from rhubarb.errors import RhubarbException, RhubarbValidationError

Elem = TypeVar("Elem")


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


@total_ordering
class RhubarbPhoneNumber(phonenumbers.PhoneNumber):
    """
    Borrowed from django-phonenumber-field.

    A extended version of phonenumbers.PhoneNumber that provides
    some neat and more pythonic, easy to access methods. This makes using a
    PhoneNumber instance much easier, especially in templates and such.
    """

    format_map = {
        "E164": phonenumbers.PhoneNumberFormat.E164,
        "INTERNATIONAL": phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        "NATIONAL": phonenumbers.PhoneNumberFormat.NATIONAL,
        "RFC3966": phonenumbers.PhoneNumberFormat.RFC3966,
    }

    @classmethod
    def from_string(cls, phone_number, region=None):
        """
        :arg str phone_number: parse this :class:`str` as a phone number.
        :keyword str region: 2-letter country code as defined in ISO 3166-1.
            When not supplied, defaults to :setting:`PHONENUMBER_DEFAULT_REGION`
        """
        phone_number_obj = cls()
        if region is None:
            region = None
        phonenumbers.parse(
            number=phone_number,
            region=region,
            keep_raw_input=True,
            numobj=phone_number_obj,
        )
        return phone_number_obj

    def __str__(self):
        if self.is_valid():
            format_string = "E164"
            fmt = self.format_map[format_string]
            return self.format_as(fmt)
        else:
            return self.raw_input

    def __repr__(self):
        if not self.is_valid():
            return f"Invalid{type(self).__name__}(raw_input={self.raw_input})"
        return super().__repr__()

    def is_valid(self):
        """
        Whether the number supplied is actually valid.

        :return: ``True`` when the phone number is valid.
        :rtype: bool
        """
        return phonenumbers.is_valid_number(self)

    def format_as(self, format):
        return phonenumbers.format_number(self, format)

    @property
    def as_international(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    @property
    def as_e164(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.E164)

    @property
    def as_national(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.NATIONAL)

    @property
    def as_rfc3966(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.RFC3966)

    def __len__(self):
        return len(str(self))

    def __eq__(self, other):
        """
        Override parent equality because we store only string representation
        of phone number, so we must compare only this string representation
        """
        if other in validators.EMPTY_VALUES:
            return False
        elif isinstance(other, str):
            default_region = getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)
            other = to_python(other, region=default_region)
        elif isinstance(other, type(self)):
            # Nothing to do. Good to compare.
            pass
        elif isinstance(other, phonenumbers.PhoneNumber):
            # The parent class of PhoneNumber does not have .is_valid().
            # We need to make it match ours.
            old_other = other
            other = type(self)()
            other.merge_from(old_other)
        else:
            return False

        format_string = "E164"
        fmt = self.format_map[format_string]
        self_str = self.format_as(fmt) if self.is_valid() else self.raw_input
        other_str = other.format_as(fmt) if other.is_valid() else other.raw_input
        return self_str == other_str

    def __lt__(self, other):
        if isinstance(other, phonenumbers.PhoneNumber):
            old_other = other
            other = type(self)()
            other.merge_from(old_other)
        elif not isinstance(other, type(self)):
            raise TypeError(
                "'<' not supported between instances of "
                "'%s' and '%s'" % (type(self).__name__, type(other).__name__)
            )

        invalid = None
        if not self.is_valid():
            invalid = self
        elif not other.is_valid():
            invalid = other
        if invalid is not None:
            raise ValueError("Invalid phone number: %r" % invalid)

        format_string = "E164"
        fmt = self.format_map[format_string]
        return self.format_as(fmt) < other.format_as(fmt)

    def __hash__(self):
        return hash(str(self))


def parse_phone(v):
    v = str(v)
    phone_number_obj = phonenumbers.PhoneNumber()

    return RhubarbPhoneNumber.from_string(v)


PhoneNumber = scalar(
    NewType("PhoneNumber", RhubarbPhoneNumber),
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


def parse_small_int(v):
    v = int(v)
    if v >= 256:
        raise RhubarbValidationError("Invalid {v}")
    return SmallIntType(v)


SmallIntType = NewType("SmallInt", int)

SmallInt = scalar(
    SmallIntType,
    serialize=lambda v: v,
    parse_value=parse_small_int,
)


def new_ref_id() -> str:
    return str(time.monotonic_ns())[-5:]


def get_conn(info: Info) -> AsyncConnection:
    return info.context["conn"]


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


@dataclasses.dataclass(frozen=True)
class Unset:
    """Values that aren't loaded from the database"""

    def __sql__(self, builder):
        builder.write("DEFAULT")


UNSET = Unset()


def call_with_maybe_info(f, obj, info):
    sig = inspect.signature(f)
    if len(sig.parameters) == 1:
        return f(obj)
    else:
        return f(obj, info)
