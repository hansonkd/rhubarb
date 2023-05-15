import dataclasses

from arq import create_pool, ArqRedis
from arq.connections import RedisSettings

from rhubarb.pkg.redis.config import RedisConfig


pools = {}


@dataclasses.dataclass(frozen=True)
class ArqConfig:
    task_modules: list[str] = dataclasses.field(default_factory=lambda: [])
    redis: RedisConfig = dataclasses.field(default_factory=RedisConfig)

    async def get_pool(self) -> ArqRedis:
        if self in pools:
            return pools[self]
        kwargs = dataclasses.asdict(self)
        arq_redis = await create_pool(RedisSettings(**kwargs))
        pools[self] = arq_redis
        return arq_redis
