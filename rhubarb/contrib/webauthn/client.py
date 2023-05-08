import base64
import uuid

import webauthn
from psycopg import AsyncConnection
from pydantic import validator
from rhubarb import save, RhubarbException
from rhubarb.config import config
from rhubarb.contrib.redis.rate_limit import rate_limit
from rhubarb.contrib.users.models import U
from rhubarb.contrib.webauthn.models import UserAuthnKey
from rhubarb.crud import by_pk, query
from starlette.requests import Request
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    RegistrationCredential,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialRequestOptions,
    AuthenticationCredential,
)


def generate_registration_options(
    user: U, request: Request
) -> PublicKeyCredentialCreationOptions:
    user_id = user.identity
    user_name = user.username
    user_display_name = user.email
    conf = config().webauthn

    public_key = webauthn.generate_registration_options(
        rp_id=conf.rp_id,
        rp_name=conf.rp_name,
        user_id=user_id,
        user_name=user_name,
        user_display_name=user_display_name,
        authenticator_selection=conf.selection_criteria,
    )

    request.session["webauthn_register_challenge"] = base64.b64encode(
        public_key.challenge
    ).decode()
    if referer := request.headers.get("referer"):
        request.session["webauthn_register_origin"] = referer
    return public_key


def b64decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s.encode())


class CustomRegistrationCredential(RegistrationCredential):
    @validator("raw_id", pre=True)
    def convert_raw_id(cls, v: str):
        assert isinstance(v, str), "raw_id is not a string"
        return b64decode(v)

    @validator("response", pre=True)
    def convert_response(cls, data: dict):
        assert isinstance(data, dict), "response is not a dictionary"
        return {k: b64decode(v) for k, v in data.items()}


async def register_complete(
    conn: AsyncConnection,
    request: Request,
    user_id: uuid.UUID,
    credential: CustomRegistrationCredential,
) -> UserAuthnKey:
    cors = config().cors
    conf = config().webauthn

    with rate_limit(key=f"authn-{request.client.host}", max_times=5, ttl_seconds=60):
        challenge = request.session.pop("webauthn_register_challenge", None)
        if not challenge:
            raise RhubarbException(
                f"User {user_id} tried to finish registering webauthn without a challenge session"
            )

        expected_challenge = base64.b64decode(challenge.encode())
        expected_origin = request.session.pop("webauthn_register_origin", None)
        registration = webauthn.verify_registration_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=conf.rp_id,
            expected_origin=expected_origin or cors.origins,
            require_user_verification=True,
        )
        return await save(
            UserAuthnKey(
                user_id=user_id,
                public_key=registration.credential_public_key,
                sign_count=registration.sign_count,
                credential_id=registration.credential_id,
            ),
            conn,
        ).execute(one=True)


async def auth_options(
    conn: AsyncConnection, request: Request, user_id: uuid.UUID
) -> PublicKeyCredentialRequestOptions:
    conf = config().webauthn

    all_keys = await query(UserAuthnKey, conn).kw_where(user_id=user_id).as_list()

    public_key = webauthn.generate_authentication_options(
        rp_id=conf.rp_id,
        allow_credentials=[
            PublicKeyCredentialDescriptor(
                id=key.credential_id, transports=conf.transports
            )
            for key in all_keys
        ],
        user_verification=conf.authentication_user_verification,
    )
    request.session["webauthn_auth_challenge"] = base64.b64encode(
        public_key.challenge
    ).decode()
    if origin := request.headers.get("referer", None):
        request.session["webauthn_auth_origin"] = origin
    return public_key


class CustomAuthenticationCredential(AuthenticationCredential):
    @validator("raw_id", pre=True)
    def convert_raw_id(cls, v: str):
        assert isinstance(v, str), "raw_id is not a string"
        return b64decode(v)

    @validator("response", pre=True)
    def convert_response(cls, data: dict):
        assert isinstance(data, dict), "response is not a dictionary"
        return {k: b64decode(v) for k, v in data.items()}


async def auth_complete(
    conn: AsyncConnection,
    request: Request,
    credential_id: uuid.UUID,
    credential: CustomAuthenticationCredential,
):
    expected_challenge = request.session.pop("webauthn_auth_challenge", None)
    if not expected_challenge:
        raise RhubarbException(
            f"Credential {credential_id} tried to finish registering webauthn without a challenge session"
        )

    expected_challenge = base64.b64decode(expected_challenge.encode())
    origin = request.session.pop("webauthn_auth_origin", None)
    cors = config().cors
    conf = config().webauthn
    with rate_limit(key=f"authn-{request.client.host}", max_times=5, ttl_seconds=60):
        db_credential: UserAuthnKey = await by_pk(UserAuthnKey, credential_id, conn).one()

        auth = webauthn.verify_authentication_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=conf.rp_id,
            expected_origin=origin or cors.origins,
            credential_public_key=db_credential.public_key,
            credential_current_sign_count=db_credential.sign_count,
        )
        return (
            by_pk(UserAuthnKey, credential_id, conn)
            .kw_update(sign_count=auth.new_sign_count)
            .execute()
        )
