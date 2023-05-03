import importlib
import os
import dataclasses
from pathlib import Path

from rhubarb.errors import RhubarbException
from rhubarb.object_set import Registry, DEFAULT_REGISTRY


@dataclasses.dataclass
class ProgramState:
    config: "Config" = None


_program_state = ProgramState()


def init_rhubarb():
    if _program_state.config is None:
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
    else:
        raise RhubarbException("Cannot call `init_rhubarb` more than once.")


@dataclasses.dataclass(frozen=True)
class PostgresConfig:
    host: str = os.getenv("PG_HOST", "localhost")
    port: int = os.getenv("PG_PORT", 5432)
    user: str = os.getenv("PG_USER", "postgres")
    password: str = os.getenv("PG_PASSWORD", "postgres")
    dbname: str = os.getenv("PG_HOST", "postgres")


@dataclasses.dataclass(frozen=True)
class Config:
    migration_directory: Path = Path("./migrations")
    registry: Registry = dataclasses.field(default_factory=lambda: DEFAULT_REGISTRY)
    postgres: PostgresConfig = dataclasses.field(default_factory=PostgresConfig)


def config() -> Config:
    if _program_state.config is None:
        raise RhubarbException(f"Must run `init_rhubarb()` before using `config()`")
    return _program_state.config
