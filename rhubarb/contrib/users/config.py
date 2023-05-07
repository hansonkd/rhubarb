import dataclasses
import datetime
import typing
from typing import Type

if typing.TYPE_CHECKING:
    from .models import User, PhoneVerification


def default_user_factory():
    from .models import User

    return User


@dataclasses.dataclass(frozen=True)
class UserConfig:
    verification_timeout: datetime.timedelta = datetime.timedelta(minutes=15)
    user_model: Type["User"] = dataclasses.field(default_factory=default_user_factory)

