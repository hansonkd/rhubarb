import dataclasses
import datetime
import typing
from typing import Type

from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    AuthenticatorAttachment,
)

if typing.TYPE_CHECKING:
    from .models import User


def default_user_factory():
    from .models import User

    return User


@dataclasses.dataclass(frozen=True)
class UserConfig:
    verification_timeout: datetime.timedelta = datetime.timedelta(minutes=15)
    user_model: Type["User"] = dataclasses.field(default_factory=default_user_factory)
    auth_rate_limit_timeout_seconds: int = 60
    auth_rate_limit_max_attempts: int = 5
