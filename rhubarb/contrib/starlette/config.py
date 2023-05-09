import dataclasses

from rhubarb.env import list_str_env, bool_env


@dataclasses.dataclass(frozen=True)
class CorsConfig:
    origins: list[str] = dataclasses.field(
        default_factory=lambda: list_str_env(
            "ORIGINS", "http://localhost,http://localhost:8000"
        )
    )
    allow_credentials: bool = bool_env("CORS_ALLOWS_CREDENTIALS", True)
    allow_methods: list[str] = dataclasses.field(
        default_factory=lambda: list_str_env("CORS_METHODS", "*")
    )
    allow_headers: list[str] = dataclasses.field(
        default_factory=lambda: list_str_env("CORS_ALLOW_HEADERS", "*")
    )
    expose_headers: list[str] = dataclasses.field(
        default_factory=lambda: list_str_env("CORS_EXPOSE_HEADERS", "*")
    )
