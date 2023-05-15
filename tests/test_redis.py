import pytest

from rhubarb.pkg.redis.cache import cache, clear_cache, local_cache, clear_cache_key
from rhubarb.pkg.redis.rate_limit import rate_limit, RateLimitExceeded


@rate_limit(key="rate_limited", max_times=10, ttl_seconds=2)
async def rate_limited():
    pass


@cache(ttl_seconds=2)
async def cached(called: dict):
    called["called"] += 1


@local_cache(ttl_seconds=2)
async def locally_cached(called: dict):
    called["called"] += 1


@cache(ttl_seconds=2, key_arg=0)
async def cached_by_key(ip: str, called: dict):
    called["called"] += 1


@pytest.mark.asyncio
async def test_rate_limit(rhubarb):
    for x in range(10):
        await rate_limited()

    with pytest.raises(RateLimitExceeded):
        await rate_limited()


@pytest.mark.asyncio
async def test_cache(rhubarb):
    await clear_cache(cached)
    data = {"called": 0}
    await cached(data)
    assert data["called"] == 1
    await cached(data)
    assert data["called"] == 1
    await clear_cache(cached)
    await cached(data)
    assert data["called"] == 2


@pytest.mark.asyncio
async def test_local_cache(rhubarb):
    await clear_cache(locally_cached)
    data = {"called": 0}
    await locally_cached(data)
    assert data["called"] == 1
    await locally_cached(data)
    assert data["called"] == 1
    await clear_cache(locally_cached)
    await locally_cached(data)
    assert data["called"] == 2


@pytest.mark.asyncio
async def test_cached_by_key(rhubarb):
    await clear_cache(cached_by_key)
    data = {"called": 0}
    await cached_by_key("0.0.0.1", data)
    assert data["called"] == 1
    await cached_by_key("0.0.0.1", data)
    assert data["called"] == 1
    await cached_by_key("0.0.0.2", data)
    assert data["called"] == 2
    await cached_by_key("0.0.0.2", data)
    assert data["called"] == 2
    await cached_by_key("0.0.0.1", data)
    assert data["called"] == 2

    # Clear key and make sure other key is still cached...
    await clear_cache_key(cached_by_key, "0.0.0.1")
    await cached_by_key("0.0.0.1", data)
    assert data["called"] == 3
    await cached_by_key("0.0.0.2", data)
    assert data["called"] == 3

    await clear_cache(cached_by_key)
    await cached_by_key("0.0.0.2", data)
    assert data["called"] == 4
