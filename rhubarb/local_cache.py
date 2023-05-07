import inspect

from rhubarb.config import config


async def get_or_set_cache(key, default_func):
    cache = config().localcache

    try:
        return cache[key]
    except KeyError:
        val = default_func()
        if inspect.isawaitable(val):
            val = await val
        cache[key] = val
        return val
