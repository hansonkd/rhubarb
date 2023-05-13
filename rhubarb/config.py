import importlib
import logging
import os
import dataclasses
from pathlib import Path
from typing import TypeVar

from cachetools import TTLCache, Cache

from rhubarb.contrib.arq.config import ArqConfig
from rhubarb.contrib.starlette.config import CorsConfig

from rhubarb.contrib.email.config import EmailConfig
from rhubarb.contrib.postgres.config import PostgresConfig, load_postgres_config
from rhubarb.contrib.redis.config import RedisConfig, load_redis_config
from rhubarb.contrib.users.config import UserConfig
from rhubarb.contrib.sessions.config import SessionConfig
from rhubarb.contrib.audit.config import AuditConfig
from rhubarb.contrib.webauthn.config import WebAuthnConfig
from rhubarb.errors import RhubarbException
from rhubarb.migrations.utils import run_migration_checks
from rhubarb.object_set import Registry, DEFAULT_REGISTRY


@dataclasses.dataclass
class ProgramState:
    config: "Config" = None


_program_state = ProgramState()


def init_rhubarb(check=True):
    if _program_state.config is None:
        logging.basicConfig(level=logging.DEBUG)
        config_path = os.getenv("RHUBARB_CONFIG", None)
        if config_path is None:
            config_obj = Config()
        else:
            module_name, attr_name = config_path.rsplit(".", 1)

            config_module = importlib.import_module(module_name)
            config_obj = getattr(config_module, attr_name)
            if callable(config_obj):
                config_obj = config_obj()
        _program_state.config = config_obj
        if check:
            run_migration_checks(config_obj)

    else:
        raise RhubarbException("Cannot call `init_rhubarb` more than once.")


@dataclasses.dataclass(frozen=True)
class Config:
    migration_directory: Path = Path("./migrations")
    registry: Registry = dataclasses.field(default_factory=lambda: DEFAULT_REGISTRY)
    cors: CorsConfig = dataclasses.field(default_factory=CorsConfig)
    postgres: PostgresConfig = dataclasses.field(default_factory=load_postgres_config)
    redis: RedisConfig = dataclasses.field(default_factory=load_redis_config)
    users: UserConfig = dataclasses.field(default_factory=UserConfig)
    audit: AuditConfig = dataclasses.field(default_factory=AuditConfig)
    sessions: SessionConfig = dataclasses.field(default_factory=SessionConfig)
    webauthn: WebAuthnConfig = dataclasses.field(default_factory=WebAuthnConfig)
    arq: ArqConfig = dataclasses.field(default_factory=ArqConfig)
    localcache: Cache = dataclasses.field(
        default_factory=lambda: TTLCache(maxsize=1024, ttl=600)
    )
    email: EmailConfig = dataclasses.field(default_factory=lambda: EmailConfig())


C = TypeVar("C", bound=Config)


def config() -> C:
    if _program_state.config is None:
        raise RhubarbException(f"Must run `init_rhubarb()` before using `config()`")
    return _program_state.config
