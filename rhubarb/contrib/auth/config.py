import dataclasses

from rhubarb.contrib.postgres.config import PostgresConfig, load_postgres_config


oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',  # force to select account
    }
)


@dataclasses.dataclass(frozen=True)
class OAuthConfig:
    name: str
    client_id: str
    client_secret: str
    client_kwargs: dict
    server_metadata_url: str | None = None


@dataclasses.dataclass(frozen=True)
class AuthConfig:
    oauth_backends: list[OAuthConfig]
    oauth: OAuth = dataclasses.field(init=False)
