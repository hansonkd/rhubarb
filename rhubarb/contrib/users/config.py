import dataclasses
import datetime
import typing
from typing import Type

if typing.TYPE_CHECKING:
    from .models import User


def default_model_factory():
    from .models import User

    return User


@dataclasses.dataclass(frozen=True)
class UserConfig:
    user_model: Type["User"] = dataclasses.field(default_factory=default_model_factory)
    num_sms_verification_digits: int = 6
    verification_timeout: datetime.timedelta = datetime.timedelta(minutes=15)
