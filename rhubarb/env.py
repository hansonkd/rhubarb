import os


def str_env(key: str, default=None) -> str | None:
    return os.getenv(key, default)


def bool_env(key: str, default=None) -> bool | None:
    v = os.getenv(key, default)
    if v is not None and isinstance(v, str):
        return v.lower() in ("true", "t", "1")
    return v


def int_env(key: str, default=None) -> int | None:
    v = os.getenv(key, default)
    if v is not None:
        return int(v)
    return v


def float_env(key: str, default=None) -> float | None:
    v = os.getenv(key, default)
    if v is not None:
        return float(v)
    return v
