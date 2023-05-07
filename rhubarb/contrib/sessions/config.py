import dataclasses

from rhubarb.contrib.redis.config import RedisConfig, load_redis_config
from rhubarb.env import str_env, int_env, bool_env


@dataclasses.dataclass(frozen=True)
class SessionConfig:
    secret_key: str = str_env("SECRET_KEY")
    cookie_name: str = str_env("SESSION_COOKIE_NAME", "session")
    max_age: int = int_env("SESSION_MAX_AGE", 24 * 60 * 60)  # One day
    same_site: str = str_env("SESSION_SAME_SITE", "lax")
    https_only: str = bool_env("SESSION_HTTPS_ONLY", False)
    domain: str | None = str_env("SESSION_DOMAIN", None)
    redis: RedisConfig = dataclasses.field(
        default_factory=lambda: load_redis_config("REDIS_SESSIONS_URI")
    )
