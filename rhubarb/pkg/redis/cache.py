import functools
import inspect
import pickle
from typing import TypeVar, Generic, Callable

import cachetools

from rhubarb import RhubarbException
from rhubarb.pkg.redis.connection import connection


V = TypeVar("V")
ONE_HOUR_SECONDS = 60 * 60


class RedisCacher(Generic[V]):
    def __init__(
        self, ttl_seconds: int = ONE_HOUR_SECONDS, key_prefix: str = "_cache_"
    ):
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds

    async def for_key(self, key: str, default_fn: Callable[[], V]) -> V:
        full_key = f"{self.key_prefix}{key}"
        async with connection() as conn:
            if val := await conn.get(full_key):
                return pickle.loads(val)
            val = default_fn()
            if inspect.isawaitable(val):
                val = await val

        async with connection() as conn:
            await conn.set(full_key, pickle.dumps(val), ex=self.ttl_seconds)
            return val

    async def clear(self):
        async with connection() as conn:
            if keys := await conn.keys(f"{self.key_prefix}*"):
                await conn.delete(*keys)

    async def clear_key(self, key: str):
        async with connection() as conn:
            await conn.delete(f"{self.key_prefix}{key}")


class LocalRedisCacher(RedisCacher):
    def __init__(
        self,
        ttl_seconds: int = ONE_HOUR_SECONDS,
        key_prefix: str = "_cache_",
        local_cache: cachetools.Cache = None,
        local_only=False,
        max_size=1024,
    ):
        self.local_cache = local_cache or cachetools.TTLCache(
            maxsize=max_size, ttl=ttl_seconds
        )
        self.local_only = local_only
        super().__init__(ttl_seconds=ttl_seconds, key_prefix=key_prefix)

    async def for_key(self, key: str, default_fn: Callable[[], V]) -> V:
        if key in self.local_cache:
            return self.local_cache[key]
        if self.local_only:
            v = default_fn()
            if inspect.isawaitable(v):
                v = await v
        else:
            v = await super().for_key(key, default_fn)
        self.local_cache[key] = v
        return v

    async def clear(self):
        self.local_cache.clear()
        return await super().clear()

    async def clear_key(self, key: str):
        if key in self.local_cache:
            del self.local_cache[key]
        return await super().clear_key(key)


def cache(
    ttl_seconds: int = ONE_HOUR_SECONDS,
    prefix: str = None,
    key_arg: int | str = None,
    cacher_cls=RedisCacher,
    **kwargs,
):
    def decorator(f):
        if prefix is None:
            prefixed = f"{f.__name__}_"
        else:
            prefixed = prefix

        cacher = cacher_cls(ttl_seconds=ttl_seconds, key_prefix=prefixed, **kwargs)

        @functools.wraps(f, assigned="_cacher")
        async def wrapper(*args, **kwargs):
            def default_fn():
                return f(*args, **kwargs)

            if key_arg is None:
                key = ""
            elif isinstance(key_arg, int):
                key = str(args[key_arg])
            elif isinstance(key_arg, str):
                key = str(kwargs[key_arg])
            else:
                raise RhubarbException(
                    f"Invalid cache `key_arg` {key_arg}. Must be int or str."
                )
            return await cacher.for_key(key, default_fn)

        wrapper._cacher = cacher
        return wrapper

    return decorator


local_cache = functools.partial(cache, cacher_cls=LocalRedisCacher)
local_only_cache = functools.partial(
    cache, cacher_cls=LocalRedisCacher, local_only=True
)


async def clear_cache(f):
    if cacher := getattr(f, "_cacher", None):
        return await cacher.clear()
    raise RhubarbException(f"Function {f} was not wrapped by cache")


async def clear_cache_key(f, key: str):
    if cacher := getattr(f, "_cacher", None):
        return await cacher.clear_key(key)
    raise RhubarbException(f"Function {f} was not wrapped by cache")
