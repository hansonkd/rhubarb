from rhubarb.config import config


class RedisCache:
    def set(self, key, value, ttl: int = None):
        pool = await config().redis.get_pool()
        pool.set()
