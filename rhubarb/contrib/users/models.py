import dataclasses
import datetime
import secrets
import string
import uuid
import random
from typing import Optional

from psycopg import AsyncConnection

from rhubarb import (
    PhoneNumber,
    Email,
    Constraint,
    ModelSelector,
    column,
    BaseModel,
    query,
    references,
    save, Registry, table,
)
from rhubarb.config import config
from rhubarb.functions import is_null
from rhubarb.password import Password, PasswordHash
from rhubarb.model import BaseUpdatedAtModel
from rhubarb.permission_classes import IsSuperUser

user_registry = Registry(prefix="users_")


@dataclasses.dataclass
class User(BaseUpdatedAtModel):
    username: str = column()
    first_name: Optional[str] = column(sql_default=None)
    last_name: Optional[str] = column(sql_default=None)
    password: Optional[Password] = column(sql_default=None, permission_classes=[IsSuperUser])
    email: Optional[Email] = column(sql_default=None)
    phone_number: Optional[PhoneNumber] = column(sql_default=None)
    activated: Optional[datetime.datetime] = column(sql_default=None)
    opt_in_communication_email: Optional[datetime.datetime] = column(sql_default=None)
    opt_in_communication_sms: Optional[datetime.datetime] = column(sql_default=None)
    last_login: Optional[datetime.datetime] = column(sql_default=None)
    is_staff: bool = column(sql_default=False)
    is_superuser: bool = column(sql_default=False)

    def __post_init__(self):
        if isinstance(self.password, bytes):
            self.password = PasswordHash(self.password)
        if isinstance(self.phone_number, str):
            self.password = PhoneNumber(self.phone_number)

    def __constraints__(self: ModelSelector):
        return {
            "unique_username": Constraint(check=self.username, unique=True),
            "unique_phone_number": Constraint(check=self.phone_number, unique=True),
            "unique_email": Constraint(check=self.email, unique=True),
        }


@dataclasses.dataclass
class VerificationMixin(BaseModel):
    sent: Optional[datetime.datetime] = column(sql_default=None)
    user_id: uuid.UUID = references(
        lambda: config().users.user_model.__table__, on_delete="CASCADE"
    )
    verified: Optional[datetime.datetime] = column()
    canceled: Optional[datetime.datetime] = column()


def random_digits():
    return "".join(random.choices(string.digits, k=6))


def random_token():
    return secrets.token_urlsafe(24)


@table(registry=user_registry)
class PhoneVerification(VerificationMixin):
    phone_number: PhoneNumber = column()
    code: str = column(default_factory=random_digits)


@table(registry=user_registry)
class EmailVerification(VerificationMixin):
    email: Email = column()
    code: str = column(default_factory=random_token)


@table(registry=user_registry)
class ResetPasswordVerification(VerificationMixin):
    code: str = column(default_factory=random_token)


async def get_user(conn, user_id):
    UserModel = config().users.user_model

    return await query(UserModel, conn).where(lambda x: x.id == user_id).one()


async def get_and_complete_verification(cls, conn, verification_id, code):
    time_delta = config().users.verification_timeout
    last_valid_time = datetime.datetime.utcnow() - time_delta

    def set_fn(m):
        m.verified = datetime.datetime.utcnow()

    return (
        await query(cls, conn)
        .where(
            lambda x: x.id == verification_id
            and x.code == code
            and x.sent > last_valid_time
            and is_null(x.canceled)
            and is_null(x.verified)
        )
        .update(set_fn)
        .execute(one=True)
    )


@dataclasses.dataclass
class RegistrationResult:
    user: User
    phone_verification: Optional[PhoneVerification]
    email_verification: Optional[EmailVerification]


async def register(
    conn: AsyncConnection, **kwargs
) -> RegistrationResult:
    UserModel = config().users.user_model
    password = kwargs.pop("password", None)
    if isinstance(password, str):
        kwargs["password"] = PasswordHash.new(password)
    elif isinstance(password, PasswordHash):
        kwargs["password"] = password
    new_user: User = await save(UserModel(**kwargs), conn).execute()
    email_verification = None
    phone_verification = None

    if new_user.email:
        email_verification = await set_email(conn, new_user, new_user.email)

    if new_user.phone_number:
        phone_verification = await set_phone_number(conn, new_user, new_user.phone_number)
    return RegistrationResult(user=new_user, email_verification=email_verification, phone_verification=phone_verification)


async def set_email(
    conn: AsyncConnection, user: User, new_email: str, mark_sent=True
) -> EmailVerification:
    verif = EmailVerification(user_id=user.id, email=new_email)
    if mark_sent:
        verif.sent = datetime.datetime.utcnow()
    await query(EmailVerification, conn).kw_where(user_id=user.id).kw_update(canceled=datetime.datetime.utcnow()).execute()
    return await save(verif, conn).execute()


async def set_phone_number(
    conn: AsyncConnection, user: User, phone_number: PhoneNumber, mark_sent=True
) -> PhoneVerification:
    verif = PhoneVerification(user_id=user.id, phone_number=phone_number)
    if mark_sent:
        verif.sent = datetime.datetime.utcnow()
    return await save(verif, conn).execute()


async def reset_password(
    conn: AsyncConnection, user: User, mark_sent=True
) -> ResetPasswordVerification:
    verif = ResetPasswordVerification(user_id=user.id)
    if mark_sent:
        verif.sent = datetime.datetime.utcnow()
    return await save(verif, conn).execute()


async def verify_email(
    conn: AsyncConnection, verification_id: uuid.UUID, code: str, update_user=False
) -> Optional[User]:
    if verification := await get_and_complete_verification(
        EmailVerification, conn, verification_id, code
    ):
        user = await get_user(conn, verification.user_id)
        if update_user:
            user.email = verification.email
            return await save(user, conn).execute()
        return user


async def verify_phone(
    conn: AsyncConnection, verification_id: uuid.UUID, code: str, update_user=False
) -> Optional[User]:
    if verification := await get_and_complete_verification(
        EmailVerification, conn, verification_id, code
    ):
        user = await get_user(conn, verification.user_id)
        if update_user:
            user.phone_number = verification.phone_number
            return await save(user, conn).execute()
        return user


async def verify_password_reset(
    conn: AsyncConnection, verification_id: uuid.UUID, code: str
) -> bool:
    if verification := await get_and_complete_verification(
        ResetPasswordVerification, conn, verification_id, code
    ):
        return True


async def set_password(
    conn: AsyncConnection, user: User, new_password: str
) -> User:
    user.password = PasswordHash.new(new_password)
    return await save(user, conn).execute()

