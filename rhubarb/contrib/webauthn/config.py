import dataclasses

from rhubarb.env import str_env
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    AuthenticatorTransport,
)


def default_selection_criteria():
    return AuthenticatorSelectionCriteria(
        authenticator_attachment=AuthenticatorAttachment.PLATFORM,
        resident_key=ResidentKeyRequirement.PREFERRED,
        user_verification=UserVerificationRequirement.PREFERRED,
    )


@dataclasses.dataclass(frozen=True)
class WebAuthnConfig:
    rp_id: str = str_env("WEBAUTHN_RP_ID", "localhost")
    rp_name: str = str_env("WEBAUTHN_RP_NAME", "localhost")
    selection_criteria: AuthenticatorSelectionCriteria = dataclasses.field(
        default_factory=default_selection_criteria
    )
    transports: list[AuthenticatorTransport] = dataclasses.field(
        default_factory=lambda: [AuthenticatorTransport.INTERNAL]
    )
    authentication_user_verification: UserVerificationRequirement = (
        UserVerificationRequirement.REQUIRED
    )
