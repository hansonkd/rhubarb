import uuid

from rhubarb import Registry, table, references, column
from rhubarb.config import config
from rhubarb.model import BaseUpdatedAtModel

webauthn_registry = Registry()


@table(registry=webauthn_registry)
class UserAuthnKey(BaseUpdatedAtModel):
    user_id: uuid.UUID = references(
        lambda: config().users.user_model.__table__, on_delete="CASCADE"
    )
    public_key: bytes = column()
    sign_count: int = column()
    credential_id: bytes = column()
