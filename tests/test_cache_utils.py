import pytest

import holonet.utils.cache as cache_mod
from holonet.utils.cache import TTLCache, build_cache


def test_ttl_cache_get_set_and_expire(monkeypatch):
    now = 1000.0

    def fake_time():
        return now

    monkeypatch.setattr(cache_mod.time, "time", fake_time)

    cache = TTLCache(ttl_seconds=1, max_entries=10)
    cache.set("k", {"v": 1})
    assert cache.get("k")["v"] == 1
    now += 2.0
    assert cache.get("k") is None


def test_ttl_cache_eviction():
    cache = TTLCache(ttl_seconds=60, max_entries=1)
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.get("a") is None
    assert cache.get("b") == 2


def test_build_cache_local():
    cache = build_cache(ttl_seconds=10, max_entries=2, backend="inmemory", redis_url=None)
    cache.set("x", 1)
    assert cache.get("x") == 1
    cache.clear()


def test_build_cache_redis_requires_url():
    with pytest.raises(RuntimeError):
        build_cache(ttl_seconds=10, max_entries=2, backend="redis", redis_url=None)


def test_build_cache_redis(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.store = {}

        def get(self, key):
            return self.store.get(key)

        def setex(self, key, ttl, value):
            self.store[key] = value

        def flushdb(self):
            self.store.clear()

    import redis

    fake = FakeRedis()
    monkeypatch.setattr(redis.Redis, "from_url", lambda *args, **kwargs: fake)

    cache = build_cache(
        ttl_seconds=10, max_entries=1, backend="redis", redis_url="redis://localhost:6379/0"
    )
    cache.set("a", 1)
    assert cache.get("a") == 1
