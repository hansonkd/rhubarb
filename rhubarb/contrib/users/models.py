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
    save,
)
from rhubarb.config import config
from rhubarb.core import Password
from rhubarb.model import BaseUpdatedAtModel
from rhubarb.permission_classes import IsSuperUser


class User(BaseUpdatedAtModel):
    username: str
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

    def __constraints__(self: ModelSelector):
        return {
            "unique_username": Constraint(check=self.username, unique=True),
            "unique_phone_number": Constraint(check=self.phone_number, unique=True),
            "unique_email": Constraint(check=self.email, unique=True),
        }


@dataclasses.dataclass
class VerificationMixin(BaseModel):
    sent: datetime.datetime = column()
    user_id: uuid.UUID = references(
        lambda: config().users.user_model.__table__, on_delete="CASCADE"
    )
    verified: Optional[datetime.datetime] = column()
    canceled: Optional[datetime.datetime] = column()


def random_digits():
    num_digits = config().users.num_sms_verification_digits
    return "".join(random.choices(string.digits, k=num_digits))


@dataclasses.dataclass
class PhoneVerification(VerificationMixin):
    phone_number: PhoneNumber = column()
    code: str = column()


@dataclasses.dataclass
class EmailVerification(VerificationMixin):
    email: Email = column()
    code: str = column()


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
        )
        .update(set_fn)
        .execute(one=True)
    )


async def verify_email(
    conn: AsyncConnection, verification_id: uuid.UUID, code: str, update_user=False
) -> Optional[User]:
    if verification := await get_and_complete_verification(
        EmailVerification, conn, verification_id, code
    ):
        user = await get_user(verification.user_id, conn)
        if update_user:
            user.email = verification.email
            return await save(user, conn)
        return user


async def verify_phone(
    conn: AsyncConnection, verification_id: uuid.UUID, code: str, update_user=False
) -> Optional[User]:
    if verification := await get_and_complete_verification(
        EmailVerification, conn, verification_id, code
    ):
        user = await get_user(verification.user_id, conn)
        if update_user:
            user.phone_number = verification.phone_number
            return await save(user, conn)
        return user
